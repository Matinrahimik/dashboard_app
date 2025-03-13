# Survey Data Visualization Dashboard

A data visualization dashboard for survey responses, packaged as a standalone macOS application.

## Quick Start for Non-Technical Users

If you want to create a simple, single-file application for a friend with limited technical knowledge:

1. Navigate to the `dashboardapp` directory in Terminal
2. Run the all-in-one script:

```bash
./make_app_for_friend.sh
```

3. This will create a DMG file that you can share with your friend
4. Your friend just needs to:
   - Double-click the DMG to open it
   - Drag the app to their Applications folder (or anywhere they want)
   - Double-click the app to run it

## Features

- Interactive visualizations of survey data
- Filter by demographics (age, gender, region, etc.)
- Multiple chart types (bar, pie, donut, etc.)
- Text response analysis

## Advanced Options

### Option 1: Run the pre-built application

1. Navigate to the `dashboardapp` directory
2. Double-click the `run_dashboard.command` file
3. If the application is not built yet, it will run in Python mode

### Option 2: Build the application

1. Navigate to the `dashboardapp` directory in Terminal
2. Run the build script:

```bash
./build_app.sh
```

3. After building, you can find the application at `dist/DashboardApp.app`
4. Double-click the application to run it

## Compatibility

This application is compatible with:
- macOS 10.15 (Catalina) and newer
- Both Intel and Apple Silicon (M1/M2/M3) Macs

## Troubleshooting

If you encounter any issues:

1. Make sure all the data files are in the same directory as the application
2. Check that you have an active internet connection (for the first run)
3. If the application doesn't open automatically, manually navigate to http://localhost:8050 in your web browser
4. Run the `check_files.py` script to verify that all required files are present:

```bash
python dashboardapp/check_files.py
```

## Distribution

To create a distributable DMG file:

1. Build the application first using `build_app.sh`
2. Run the packaging script:

```bash
./dashboardapp/package_app.sh
```

3. Share the resulting `DashboardApp.dmg` file with others

## Data Files

The application requires the following data files:
- Chat Data Text.xlsx
- Chat Data Numeric.xlsx
- Questions.xlsx 