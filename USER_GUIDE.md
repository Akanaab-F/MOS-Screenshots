# User Guide - Route Screenshot Generator

## Quick Start Guide

### Step 1: Access the System
1. Open your web browser (Chrome, Firefox, Safari, or Edge)
2. Go to the URL provided by your administrator
3. You'll see the Route Screenshot Generator homepage

### Step 2: Create an Account
1. Click "Get Started" or "Register"
2. Fill in your details:
   - Username (choose something you'll remember)
   - Email address
   - Password (make it secure)
3. Click "Register"
4. You'll be automatically logged in

### Step 3: Upload Your Excel File
1. Click "Upload File" in the navigation menu
2. Prepare your Excel file with the required format (see below)
3. Drag and drop your file into the upload area, or click "Choose File"
4. Click "Start Processing"

### Step 4: Monitor Progress
1. Go to your Dashboard
2. You'll see your job listed with a progress bar
3. The status will show:
   - **Pending**: Waiting to start
   - **Processing**: Currently working on your file
   - **Completed**: Ready for download
   - **Failed**: Something went wrong

### Step 5: Download Results
1. When the job shows "Completed", click the "Download" button
2. Save the ZIP file to your computer
3. Extract the ZIP file to access all your route screenshots

## Excel File Requirements

Your Excel file must have exactly 3 sheets with specific column names:

### Sheet 1: "transportation"
| Column Name | What to put here |
|-------------|------------------|
| ID | A unique name or number for each site |
| latitude | The latitude coordinate of the site |
| longitude | The longitude coordinate of the site |
| warehouse | The name of the warehouse (must match the warehouse sheet) |

### Sheet 2: "warehouse"
| Column Name | What to put here |
|-------------|------------------|
| Warehouse | The name of the warehouse |
| latitude | The latitude coordinate of the warehouse |
| longitude | The longitude coordinate of the warehouse |

### Sheet 3: "region"
| Column Name | What to put here |
|-------------|------------------|
| region | The name of the region |
| warehouse | The warehouse name (must match the warehouse sheet) |

## Example Excel File

Here's what your Excel file should look like:

**transportation sheet:**
```
ID      | latitude  | longitude | warehouse
Site001 | 40.7128   | -74.0060  | NYC_Warehouse
Site002 | 34.0522   | -118.2437 | LA_Warehouse
```

**warehouse sheet:**
```
Warehouse      | latitude  | longitude
NYC_Warehouse  | 40.7589   | -73.9851
LA_Warehouse   | 34.0522   | -118.2437
```

**region sheet:**
```
region | warehouse
East   | NYC_Warehouse
West   | LA_Warehouse
```

## Tips for Success

### File Format
- Use Excel format (.xlsx or .xls)
- Make sure column names are exactly as shown above
- Don't use spaces in column names
- Keep file size under 16MB

### Coordinates
- Use decimal format (e.g., 40.7128, not 40°42'46"N)
- Make sure coordinates are accurate
- Test a few coordinates on Google Maps first

### Processing Time
- Small files (10-50 routes): 5-15 minutes
- Medium files (50-200 routes): 15-60 minutes
- Large files (200+ routes): 1-3 hours

## Troubleshooting

### Common Issues

**"Invalid file type" error**
- Make sure you're uploading an Excel file (.xlsx or .xls)
- Check that the file isn't corrupted

**"Missing warehouse" error**
- Check that warehouse names in the transportation sheet exactly match the warehouse sheet
- Make sure there are no extra spaces in the names

**"Job failed" status**
- Check that all required columns are present
- Verify that coordinates are in the correct format
- Try with a smaller test file first

**Screenshots are blank**
- This usually means the route couldn't be found
- Check that coordinates are accurate
- Try testing the coordinates on Google Maps manually

### Getting Help

If you're having trouble:
1. Check this guide first
2. Ask your administrator for help
3. Try with a simple test file first
4. Make sure your internet connection is stable

## What You Get

After processing, you'll receive:
- A ZIP file containing all route screenshots
- Each screenshot shows the driving route from site to warehouse
- File names include the site ID for easy identification
- High-quality images suitable for reports and presentations

## Best Practices

1. **Test first**: Try with a small file (5-10 routes) before processing large files
2. **Check coordinates**: Verify coordinates are accurate before uploading
3. **Use consistent naming**: Use clear, consistent names for sites and warehouses
4. **Backup your data**: Keep a copy of your original Excel file
5. **Plan ahead**: Large files take time to process, plan accordingly

## Need More Help?

Contact your system administrator or IT support team for technical assistance. 