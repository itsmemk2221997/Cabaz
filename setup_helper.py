#!/usr/bin/env python3
"""
CABAS Setup Helper
Helps locate CABAS executable and update configuration
"""

import os
import json
import glob
from pathlib import Path
from config_manager import ConfigManager

def find_cabas_executable():
    """
    Search for CABAS executable in common locations
    
    Returns:
        list: List of found executable paths
    """
    possible_paths = [
        r"C:\Program Files\CabgroupCSP\CabgroupCSP.exe",
        r"C:\Program Files (x86)\CabgroupCSP\CabgroupCSP.exe",
        r"C:\Program Files\CABAS\CABAS.exe",
        r"C:\Program Files (x86)\CABAS\CABAS.exe",
        r"C:\Program Files\CAB\*.exe",
        r"C:\Program Files (x86)\CAB\*.exe",
    ]
    
    found_paths = []
    
    print("Searching for CABAS executable...")
    
    for path_pattern in possible_paths:
        if '*' in path_pattern:
            # Use glob for wildcard patterns
            matches = glob.glob(path_pattern)
            for match in matches:
                if os.path.isfile(match) and match.lower().endswith('.exe'):
                    found_paths.append(match)
                    print(f"Found: {match}")
        else:
            # Direct path check
            if os.path.isfile(path_pattern):
                found_paths.append(path_pattern)
                print(f"Found: {path_pattern}")
    
    # Search in common program directories
    program_dirs = [
        r"C:\Program Files",
        r"C:\Program Files (x86)"
    ]
    
    for program_dir in program_dirs:
        if os.path.exists(program_dir):
            # Search for directories containing 'cab' or 'csp'
            for root, dirs, files in os.walk(program_dir):
                dir_name = os.path.basename(root).lower()
                if any(keyword in dir_name for keyword in ['cab', 'csp']):
                    for file in files:
                        if file.lower().endswith('.exe') and any(keyword in file.lower() for keyword in ['cab', 'csp']):
                            full_path = os.path.join(root, file)
                            if full_path not in found_paths:
                                found_paths.append(full_path)
                                print(f"Found: {full_path}")
    
    return found_paths

def update_config_with_path(exe_path):
    """
    Update configuration file with CABAS executable path
    
    Args:
        exe_path: Path to CABAS executable
    """
    try:
        config_manager = ConfigManager()
        
        # Update the path (convert backslashes for JSON)
        json_safe_path = exe_path.replace('\\', '\\\\')
        config_manager.set('cabas.exe_path', json_safe_path)
        
        if config_manager.save_config():
            print(f"✅ Configuration updated successfully!")
            print(f"CABAS executable path set to: {exe_path}")
            return True
        else:
            print("❌ Failed to save configuration")
            return False
            
    except Exception as e:
        print(f"❌ Error updating configuration: {e}")
        return False

def test_cabas_path(exe_path):
    """
    Test if CABAS executable can be launched
    
    Args:
        exe_path: Path to test
        
    Returns:
        bool: True if path is valid and executable
    """
    try:
        if not os.path.isfile(exe_path):
            return False
        
        # Check if file is executable
        if not os.access(exe_path, os.X_OK):
            return False
        
        return True
        
    except Exception:
        return False

def main():
    """
    Main setup helper function
    """
    print("\n" + "="*60)
    print("CABAS Setup Helper")
    print("="*60)
    
    # Find CABAS executables
    found_paths = find_cabas_executable()
    
    if not found_paths:
        print("\n❌ No CABAS executable found automatically.")
        print("\nPlease manually locate your CABAS executable and update config.json:")
        print("1. Find CABAS shortcut on desktop or Start menu")
        print("2. Right-click → Properties")
        print("3. Copy the 'Target' path")
        print("4. Update 'cabas.exe_path' in config.json")
        return
    
    print(f"\n✅ Found {len(found_paths)} potential CABAS executable(s):")
    
    # Test each path
    valid_paths = []
    for i, path in enumerate(found_paths, 1):
        print(f"\n{i}. {path}")
        if test_cabas_path(path):
            print("   ✅ Valid executable")
            valid_paths.append(path)
        else:
            print("   ❌ Invalid or inaccessible")
    
    if not valid_paths:
        print("\n❌ No valid CABAS executables found.")
        return
    
    # Let user choose if multiple valid paths
    if len(valid_paths) == 1:
        selected_path = valid_paths[0]
        print(f"\nUsing: {selected_path}")
    else:
        print(f"\nMultiple valid executables found. Please choose:")
        for i, path in enumerate(valid_paths, 1):
            print(f"{i}. {path}")
        
        while True:
            try:
                choice = input(f"\nEnter choice (1-{len(valid_paths)}): ").strip()
                choice_idx = int(choice) - 1
                if 0 <= choice_idx < len(valid_paths):
                    selected_path = valid_paths[choice_idx]
                    break
                else:
                    print("Invalid choice. Please try again.")
            except ValueError:
                print("Please enter a valid number.")
    
    # Update configuration
    if update_config_with_path(selected_path):
        print("\n🎉 Setup complete! You can now run:")
        print("   python main.py interactive")
        print("\nTo test the CABAS automation system.")
    else:
        print("\n❌ Setup failed. Please manually update config.json")

if __name__ == "__main__":
    main()