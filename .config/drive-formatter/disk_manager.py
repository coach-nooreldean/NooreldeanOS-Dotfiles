import subprocess
import json
import logging

def get_available_drives():
    """
    Get a list of available disks and their partitions that can be formatted.
    We exclude disks containing partitions mounted on / or /boot.
    """
    try:
        # Run lsblk to get JSON output
        result = subprocess.run(
            ['lsblk', '-J', '-o', 'KNAME,PATH,MODEL,SIZE,TYPE,MOUNTPOINTS,RM'],
            capture_output=True, text=True, check=True
        )
        data = json.loads(result.stdout)
        
        # Separate disks and partitions
        disks = []
        partitions = []
        for device in data.get('blockdevices', []):
            if device.get('type') == 'disk':
                disks.append(device)
            elif device.get('type') == 'part' or device.get('type') == 'part':
                partitions.append(device)
                
        available_disks = []
        
        for disk in disks:
            disk_kname = disk.get('kname', '')
            # Ignore zram and loop devices
            if disk_kname.startswith('zram') or disk_kname.startswith('loop'):
                continue
                
            # Find all partitions for this disk
            disk_parts = [p for p in partitions if p.get('kname', '').startswith(disk_kname)]
            
            # Check if it's a system disk (mounted on / or /boot)
            is_system_disk = False
            all_mps = list(disk.get('mountpoints', []))
            for p in disk_parts:
                all_mps.extend(p.get('mountpoints', []))
                
            if any(mp in ['/', '/boot', '/boot/efi'] for mp in all_mps if mp):
                continue
                
            path = disk.get('path', f'/dev/{disk_kname}')
            size = disk.get('size', 'Unknown')
            model = disk.get('model', 'Unknown Drive')
            if not model:
                model = 'Unknown Drive'
            rm = disk.get('rm', False)
            
            disk_name = f"{model} ({path}) - {size}"
            if rm:
                disk_name = f"[USB/Removable] {disk_name}"
                
            disk_info = {
                'path': path,
                'display_name': disk_name,
                'partitions': []
            }
            
            for p in disk_parts:
                p_kname = p.get('kname', '')
                p_path = p.get('path', f'/dev/{p_kname}')
                p_size = p.get('size', 'Unknown')
                p_mps = p.get('mountpoints', [])
                disk_info['partitions'].append({
                    'path': p_path,
                    'display_name': f"Partition {p_kname} - {p_size}",
                    'is_mounted': any(mp for mp in p_mps if mp)
                })
                
            available_disks.append(disk_info)
            
        return available_disks
    except Exception as e:
        logging.error(f"Error getting drives: {e}")
        return []

def format_drive(device_path, fs_type, label="", password=""):
    """
    Format a drive using sudo -S for privilege escalation.
    fs_type: ext4, FAT32, NTFS, exFAT
    """
    fs_map = {
        'ext4': 'mkfs.ext4',
        'FAT32': 'mkfs.vfat',
        'NTFS': 'mkfs.ntfs',
        'exFAT': 'mkfs.exfat'
    }
    
    mkfs_cmd = fs_map.get(fs_type)
    if not mkfs_cmd:
        raise ValueError("Unsupported file system type")
        
    cmd = ['sudo', '-S', mkfs_cmd]
    
    # Add label if provided
    if label:
        if fs_type in ['ext4', 'NTFS', 'exFAT']:
            cmd.extend(['-L', label])
        elif fs_type == 'FAT32':
            cmd.extend(['-n', label])
            
    # Add force flags for some filesystems to avoid interactive prompts
    if fs_type == 'ext4':
        cmd.extend(['-F'])
    elif fs_type == 'NTFS':
        cmd.extend(['-f']) # Fast format
    elif fs_type == 'FAT32':
        cmd.extend(['-I']) # Allow formatting entire disk without partition table
        
    cmd.append(device_path)
    
    # Unmount the device and any of its partitions to avoid "Device or resource busy"
    result = subprocess.run(['lsblk', '-rno', 'PATH'], capture_output=True, text=True)
    if result.returncode == 0:
        paths = [p for p in result.stdout.splitlines() if p.startswith(device_path)]
        # Sort in reverse to unmount partitions (e.g., sda1) before the disk (sda)
        paths.sort(reverse=True)
        for p in paths:
            subprocess.run(['sudo', '-S', 'umount', p], input=(password + '\n').encode(), capture_output=True)
            
    # Wipe filesystem/partition signatures to ensure a clean slate
    subprocess.run(['sudo', '-S', 'wipefs', '-a', device_path], input=(password + '\n').encode(), capture_output=True)
    
    # Run the format command
    process = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    stdout, stderr = process.communicate(input=password + '\n')
    
    if process.returncode != 0:
        raise Exception(f"Formatting failed:\n{stderr}")
        
    return True
