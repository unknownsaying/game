// handle_disk.c – Virtual disk managed by an opaque handle
// Compile: make (see Makefile below)

#include <linux/init.h>
#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/fs.h>
#include <linux/slab.h>
#include <linux/uaccess.h>
#include <linux/cdev.h>
#include <linux/device.h>
#include <linux/vmalloc.h>

#define DISK_SECTOR_SIZE 512
#define DISK_SECTORS     1024     // 1 MB total
#define DISK_SIZE        (DISK_SECTOR_SIZE * DISK_SECTORS)

/* Opaque handle – users only see this pointer */
struct disk_handle {
    u8 *data;                     // raw storage
    size_t capacity_sectors;
    size_t sector_size;
    struct cdev cdev;
    struct device *device;
    struct class *class;
    dev_t devt;
};

static struct disk_handle *global_disk = NULL;   // for demo

/* Handle API (can be used by any kernel component) */

// Allocate a new virtual disk and return its handle
struct disk_handle *disk_create(size_t num_sectors, size_t sector_size)
{
    struct disk_handle *h;
    size_t total_size;

    if (num_sectors == 0 || sector_size == 0)
        return ERR_PTR(-EINVAL);

    total_size = num_sectors * sector_size;
    h = kzalloc(sizeof(*h), GFP_KERNEL);
    if (!h)
        return ERR_PTR(-ENOMEM);

    h->data = vzalloc(total_size);
    if (!h->data) {
        kfree(h);
        return ERR_PTR(-ENOMEM);
    }

    h->capacity_sectors = num_sectors;
    h->sector_size = sector_size;
    pr_info("handle_disk: created disk handle %p (%zu sectors)\n", h, num_sectors);
    return h;
}
EXPORT_SYMBOL(disk_create);

// Destroy the disk handle (free memory)
void disk_destroy(struct disk_handle *h)
{
    if (!h)
        return;
    vfree(h->data);
    kfree(h);
    pr_info("handle_disk: destroyed disk handle\n");
}
EXPORT_SYMBOL(disk_destroy);

// Read one sector from the handle
int disk_read_sector(struct disk_handle *h, size_t sector, u8 *buf)
{
    if (!h || !buf || sector >= h->capacity_sectors)
        return -EINVAL;
    memcpy(buf, h->data + sector * h->sector_size, h->sector_size);
    return 0;
}
EXPORT_SYMBOL(disk_read_sector);

// Write one sector to the handle
int disk_write_sector(struct disk_handle *h, size_t sector, const u8 *buf)
{
    if (!h || !buf || sector >= h->capacity_sectors)
        return -EINVAL;
    memcpy(h->data + sector * h->sector_size, buf, h->sector_size);
    return 0;
}
EXPORT_SYMBOL(disk_write_sector);

/* Character device operations (for user‑space access) */

static ssize_t hdisk_read(struct file *filp, char __user *ubuf, size_t count, loff_t *ppos)
{
    struct disk_handle *h = filp->private_data;
    loff_t pos = *ppos;
    size_t sector;
    u8 *kbuf;
    ssize_t ret = 0;

    if (!h)
        return -ENODEV;
    if (pos < 0 || pos >= h->capacity_sectors * h->sector_size)
        return 0; // EOF

    kbuf = kmalloc(h->sector_size, GFP_KERNEL);
    if (!kbuf)
        return -ENOMEM;

    sector = pos / h->sector_size;
    if (disk_read_sector(h, sector, kbuf) < 0) {
        kfree(kbuf);
        return -EIO;
    }

    if (count > h->sector_size - (pos % h->sector_size))
        count = h->sector_size - (pos % h->sector_size);

    if (copy_to_user(ubuf, kbuf + (pos % h->sector_size), count)) {
        kfree(kbuf);
        return -EFAULT;
    }

    *ppos += count;
    ret = count;
    kfree(kbuf);
    return ret;
}

static ssize_t hdisk_write(struct file *filp, const char __user *ubuf, size_t count, loff_t *ppos)
{
    struct disk_handle *h = filp->private_data;
    loff_t pos = *ppos;
    size_t sector;
    u8 *kbuf;
    ssize_t ret = 0;

    if (!h)
        return -ENODEV;
    if (pos < 0 || pos >= h->capacity_sectors * h->sector_size)
        return -ENOSPC;

    kbuf = kmalloc(h->sector_size, GFP_KERNEL);
    if (!kbuf)
        return -ENOMEM;

    sector = pos / h->sector_size;
    // Read-modify-write if we're not writing a full sector
    if (disk_read_sector(h, sector, kbuf) < 0) {
        kfree(kbuf);
        return -EIO;
    }

    if (count > h->sector_size - (pos % h->sector_size))
        count = h->sector_size - (pos % h->sector_size);

    if (copy_from_user(kbuf + (pos % h->sector_size), ubuf, count)) {
        kfree(kbuf);
        return -EFAULT;
    }

    if (disk_write_sector(h, sector, kbuf) < 0) {
        kfree(kbuf);
        return -EIO;
    }

    *ppos += count;
    ret = count;
    kfree(kbuf);
    return ret;
}

static int hdisk_open(struct inode *inode, struct file *filp)
{
    // Bind the global disk handle (or retrieve from container_of)
    filp->private_data = global_disk;
    if (!global_disk)
        return -ENODEV;
    return 0;
}

static const struct file_operations hdisk_fops = {
    .owner = THIS_MODULE,
    .read  = hdisk_read,
    .write = hdisk_write,
    .open  = hdisk_open,
};

/* Module init / exit */

static int __init handle_disk_init(void)
{
    int ret;
    dev_t dev;

    // Create the disk handle
    global_disk = disk_create(DISK_SECTORS, DISK_SECTOR_SIZE);
    if (IS_ERR(global_disk)) {
        pr_err("handle_disk: failed to create disk\n");
        return PTR_ERR(global_disk);
    }

    // Allocate a character device region
    ret = alloc_chrdev_region(&dev, 0, 1, "hdisk");
    if (ret) {
        disk_destroy(global_disk);
        return ret;
    }
    global_disk->devt = dev;

    // Create class and device
    global_disk->class = class_create("hdisk_class");
    if (IS_ERR(global_disk->class)) {
        unregister_chrdev_region(dev, 1);
        disk_destroy(global_disk);
        return PTR_ERR(global_disk->class);
    }

    global_disk->device = device_create(global_disk->class, NULL, dev, NULL, "hdisk0");
    if (IS_ERR(global_disk->device)) {
        class_destroy(global_disk->class);
        unregister_chrdev_region(dev, 1);
        disk_destroy(global_disk);
        return PTR_ERR(global_disk->device);
    }

    cdev_init(&global_disk->cdev, &hdisk_fops);
    global_disk->cdev.owner = THIS_MODULE;
    ret = cdev_add(&global_disk->cdev, dev, 1);
    if (ret) {
        device_destroy(global_disk->class, dev);
        class_destroy(global_disk->class);
        unregister_chrdev_region(dev, 1);
        disk_destroy(global_disk);
        return ret;
    }

    pr_info("handle_disk: /dev/hdisk0 ready (1 MB virtual disk)\n");
    return 0;
}

static void __exit handle_disk_exit(void)
{
    if (global_disk) {
        cdev_del(&global_disk->cdev);
        device_destroy(global_disk->class, global_disk->devt);
        class_destroy(global_disk->class);
        unregister_chrdev_region(global_disk->devt, 1);
        disk_destroy(global_disk);
        global_disk = NULL;
    }
    pr_info("handle_disk: module unloaded\n");
}

module_init(handle_disk_init);
module_exit(handle_disk_exit);

MODULE_LICENSE("GPL");
MODULE_AUTHOR("DarkGameStudio");
MODULE_DESCRIPTION("In-kernel virtual disk handle with character device interface");
