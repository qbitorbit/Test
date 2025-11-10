# ADB Agent Skills

## Best Practices for Android Device Automation

### Timing and Delays
- After launching an app, wait 2-3 seconds before interacting
- After screen transitions, wait 1-2 seconds
- Use `execute_shell_command('sleep 2')` if needed between actions

### Screen Coordinates
- Always take a screenshot first to verify screen layout
- Samsung Galaxy S24+ typical resolution: 1080x2340
- Center of screen: approximately (540, 1170)
- Top navigation: y < 200
- Bottom navigation: y > 2100

### Common Coordinates (1080x2340):
- Back button area: (100, 100)
- Home gesture area: (540, 2300)
- Status bar: (540, 50)
- Search bar (if present): (540, 300)

### App Launching
- Always use package name, not app label
- Common packages:
  - Chrome: `com.android.chrome`
  - Settings: `com.android.settings`
  - Play Store: `com.android.vending`
  - Camera: `com.sec.android.app.camera`
  - Gallery: `com.sec.android.gallery3d`

### Text Input
- Spaces must be replaced with `%s`
- Special characters may need escaping
- For complex text, consider using clipboard: `input text` then `keyevent KEYCODE_PASTE`

### Package Management
- Use `list_packages` with filter to find specific apps
- Filter examples: "chrome", "google", "samsung"
- Package names are case-sensitive

### Shell Commands
Best shell commands for common tasks:
- Get screen on/off state: `dumpsys power | grep 'Display Power: state='`
- Current activity: `dumpsys window | grep mCurrentFocus`
- Battery info: `dumpsys battery`
- Screen density: `wm density`
- Screen size: `wm size`
- List running apps: `ps | grep u0_a`

### Error Handling
- If "No device connected", always try `connect_device()` first
- If app won't launch, verify package name with `list_packages`
- If tap doesn't work, take screenshot to verify coordinates
- If text input fails, try using virtual keyboard commands

### Multi-Step Workflows
For complex tasks, break into steps:
1. Take initial screenshot
2. Launch app
3. Wait/verify
4. Perform action
5. Take final screenshot to verify

### File Operations
- Push files to `/sdcard/` for user-accessible storage
- Pull files from `/sdcard/Download/` for downloads
- Use absolute paths for file operations

### Screenshot Tips
- Always use descriptive filenames: `before_action.png`, `after_action.png`
- Screenshots automatically pulled to current directory
- Useful for debugging and verification

### Common Patterns

#### Pattern: Launch and Verify
```
1. connect_device
2. launch_app(package_name)
3. execute_shell_command('sleep 2')
4. take_screenshot('app_launched.png')
```

#### Pattern: Navigate and Tap
```
1. take_screenshot('before.png')
2. tap_screen(x, y)
3. execute_shell_command('sleep 1')
4. take_screenshot('after.png')
```

#### Pattern: Input Text
```
1. tap_screen(x, y)  # Focus on text field
2. input_text("your%stext%shere")
3. press_key("ENTER")
```

### Troubleshooting

**App won't launch:**
- Verify package name: `list_packages` with filter
- Try: `execute_shell_command('am start -n package.name/.MainActivity')`

**Text input not working:**
- Check keyboard is visible
- Try: `execute_shell_command('input text "your text"')`

**Tap not responding:**
- Verify coordinates with screenshot
- Try: `execute_shell_command('input tap x y')`

**Device disconnects:**
- Reconnect: `connect_device()`
- Check ADB connection: `execute_shell_command('echo test')`

### Performance Tips
- Batch commands when possible
- Avoid unnecessary screenshots
- Use shell commands for simple checks
- Cache device info if needed multiple times
