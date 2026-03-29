#!/bin/bash
set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}╔══════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║     FreeMind OS - BusyBox + miniarch.py по команде      ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════════════════╝${NC}"

WORK_DIR="$PWD/build"
ROOTFS_DIR="$WORK_DIR/rootfs"
ISO_DIR="$WORK_DIR/iso"
DISK_IMAGE="$WORK_DIR/freemind.img"
KERNEL_VERSION="6.1.100"
MINIARCH_SRC="$PWD/miniarch.py"

if [ ! -f "$MINIARCH_SRC" ]; then
    echo -e "${RED}❌ miniarch.py не найден!${NC}"
    exit 1
fi

echo -e "${YELLOW}[1/6] Создание папок...${NC}"
rm -rf "$WORK_DIR"
mkdir -p "$ROOTFS_DIR"/{bin,sbin,etc,proc,sys,dev,usr/bin,usr/lib,lib,lib64,home/user}
mkdir -p "$ISO_DIR"/boot/grub

echo -e "${YELLOW}[2/6] Скачивание ядра...${NC}"
if [ ! -f "$WORK_DIR/linux-$KERNEL_VERSION.tar.xz" ]; then
    wget -O "$WORK_DIR/linux-$KERNEL_VERSION.tar.xz" \
        "https://cdn.kernel.org/pub/linux/kernel/v6.x/linux-$KERNEL_VERSION.tar.xz"
fi
tar -xf "$WORK_DIR/linux-$KERNEL_VERSION.tar.xz" -C "$WORK_DIR"

echo -e "${YELLOW}[3/6] Компиляция ядра...${NC}"
cd "$WORK_DIR/linux-$KERNEL_VERSION"
make defconfig
cat >> .config << 'EOF'
CONFIG_BINFMT_SCRIPT=y
CONFIG_TMPFS=y
CONFIG_DEVTMPFS=y
CONFIG_PROC_FS=y
CONFIG_SYSFS=y
CONFIG_EXT4_FS=y
CONFIG_PRINTK=y
CONFIG_BLK_DEV_INITRD=y
CONFIG_RD_GZIP=y
CONFIG_NET=y
CONFIG_NET_IP=y
CONFIG_E1000=y
CONFIG_VIRTIO_NET=y
CONFIG_PCI=y

# Поддержка случайных чисел (RNG)
CONFIG_RANDOM_TRUST_CPU=y
CONFIG_RANDOM_TRUST_BOOTLOADER=y
CONFIG_HW_RANDOM=y
CONFIG_HW_RANDOM_VIRTIO=y
EOF
make -j$(nproc) bzImage
cp arch/x86/boot/bzImage "$ISO_DIR/boot/vmlinuz"

echo -e "${YELLOW}[4/6] Создание rootfs...${NC}"
cd "$ROOTFS_DIR"

# ===== BUSYBOX КАК INIT =====
echo -e "${YELLOW}Создание init (BusyBox shell)...${NC}"
if [ -f /bin/busybox ]; then
    cp /bin/busybox init
    cp /bin/busybox bin/sh
elif [ -f /usr/bin/busybox ]; then
    cp /usr/bin/busybox init
    cp /usr/bin/busybox bin/sh
else
    echo -e "${RED}❌ BusyBox не найден!${NC}"
    exit 1
fi
chmod +x init bin/sh

# Ссылки на команды BusyBox
mkdir -p usr/bin
cd usr/bin
for cmd in ls cat vi grep ps top mount umount cp mv rm mkdir rmdir echo ifconfig route ping netstat ip; do
    ln -sf busybox $cmd
done
ln -sf busybox udhcpc
cd ../..

# ===== PYTHON СО ВСЕМИ ЗАВИСИМОСТЯМИ =====
echo -e "${YELLOW}Копирование Python и библиотек...${NC}"

# Python
cp /usr/bin/python3 usr/bin/

# Библиотеки Python
if [ -d /usr/lib/python3.12 ]; then
    cp -r /usr/lib/python3.12 usr/lib/
elif [ -d /usr/lib/python3.11 ]; then
    cp -r /usr/lib/python3.11 usr/lib/
fi

# Динамический линковщик
cp /lib64/ld-linux-x86-64.so.2 lib64/ 2>/dev/null || \
cp /lib/x86_64-linux-gnu/ld-linux-x86-64.so.2 lib64/ 2>/dev/null

# Копируем ВСЕ библиотеки, от которых зависит Python
echo -e "${YELLOW}Копирование системных библиотек...${NC}"
for lib in libm.so.6 libc.so.6 libpthread.so.0 libdl.so.2 libutil.so.1 librt.so.1; do
    find /usr/lib -name "$lib" -exec cp {} lib/ \; 2>/dev/null
    find /lib -name "$lib" -exec cp {} lib/ \; 2>/dev/null
    find /lib64 -name "$lib" -exec cp {} lib64/ \; 2>/dev/null
done

# Дополнительные библиотеки для Python
find /usr/lib -name "libpython*.so*" -exec cp {} lib/ \; 2>/dev/null
find /usr/lib -name "libexpat*.so*" -exec cp {} lib/ \; 2>/dev/null
find /usr/lib -name "libz*.so*" -exec cp {} lib/ \; 2>/dev/null

# Твой miniarch.py
cp "$MINIARCH_SRC" usr/bin/miniarch
chmod +x usr/bin/miniarch usr/bin/python3

# ===== ПРОФИЛЬ С КОМАНДОЙ MINIARCH =====
cat > etc/profile << 'EOF'
#!/bin/sh
echo ""
echo "╔══════════════════════════════════════╗"
echo "║         FreeMind OS v0.4             ║"
echo "║      'Свобода. Простота. Контроль'   ║"
echo "╚══════════════════════════════════════╝"
echo ""
echo "Доступны команды Linux: ls, cd, cat, python3..."
echo "Для запуска Python-оболочки введите: miniarch"
echo ""
alias miniarch='/usr/bin/python3 /usr/bin/miniarch'
EOF

echo -e "${YELLOW}[5/6] Создание initramfs...${NC}"
find . | cpio -o -H newc | gzip -9 > "$ISO_DIR/boot/initramfs.img"

echo -e "${YELLOW}[6/6] Создание образа диска и ISO...${NC}"
dd if=/dev/zero of="$DISK_IMAGE" bs=1M count=1024 2>/dev/null
mkfs.ext4 -F "$DISK_IMAGE" 2>/dev/null

sudo mkdir -p /mnt/freemind
sudo mount -o loop "$DISK_IMAGE" /mnt/freemind
sudo cp -a "$ROOTFS_DIR"/* /mnt/freemind/
sudo umount /mnt/freemind
sudo rmdir /mnt/freemind

cat > "$ISO_DIR/boot/grub/grub.cfg" << 'EOF'
set default=0
set timeout=3

menuentry "FreeMind OS" {
    linux /boot/vmlinuz root=/dev/ram0 init=/init
    initrd /boot/initramfs.img
}
EOF

mkdir -p "$ISO_DIR"/install
cp "$DISK_IMAGE" "$ISO_DIR"/install/freemind.img
grub-mkrescue -o "$WORK_DIR/freemind.iso" "$ISO_DIR" 2>/dev/null

echo -e "${GREEN}✅ Готово! ISO: $WORK_DIR/freemind.iso${NC}"
ls -lh "$WORK_DIR/freemind.iso"