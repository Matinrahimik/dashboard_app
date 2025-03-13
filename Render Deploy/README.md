# Survey Dashboard Render Deployment

This folder contains all the necessary files to deploy the Survey Dashboard application to Render.

## Deployment Instructions

1. Create a new account on [Render](https://render.com/) if you don't have one already.

2. From your Render dashboard, click on "New" and select "Web Service".

3. Connect your GitHub repository or upload the files directly.

4. Configure your web service with the following settings:
   - **Name**: survey-dashboard (or any name you prefer)
   - **Environment**: Python
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:server`

5. Under the "Advanced" section, add the following environment variable:
   - **Key**: PYTHON_VERSION
   - **Value**: 3.9.0

6. Click "Create Web Service" to start the deployment process.

## File Structure

Make sure your deployment includes the following files in the root directory:

- `app.py` - The main application file
- `requirements.txt` - List of Python dependencies
- `Procfile` - Instructions for Render on how to run the app
- `Questions.xlsx` - Data file
- `Chat Data Numeric.xlsx` - Data file
- `Chat Data Text.xlsx` - Data file

## Sharing with Others

Once deployed, Render will provide you with a URL (like `https://survey-dashboard.onrender.com`). You can share this URL with anyone, and they can access your dashboard by simply clicking on the link.

## Troubleshooting

If you encounter any issues during deployment:

1. Check the build logs on Render for specific error messages
2. Ensure all data files are properly uploaded
3. Verify that the `server` variable is correctly exported in your `app.py` file
4. Make sure your Python version is compatible (3.9.0 is recommended)

For more help, refer to the [Render documentation](https://render.com/docs). 