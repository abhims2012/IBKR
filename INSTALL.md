# Installation Guide

To run this trading bot on a completely different workstation or server, you'll need to set up the environment from scratch. Since all the code is on GitHub, migrating is very straightforward. Here are the exact steps you need to take on the new machine:

## 1. Install Prerequisites
First, you need to install the core dependencies on the new Windows machine:
1. **Python**: Download and install [Python](https://www.python.org/downloads/). *(Important: Make sure to check the box that says "Add Python to PATH" during installation).*
2. **Git**: Download and install [Git for Windows](https://git-scm.com/download/win).
3. **IBKR TWS or Gateway**: Download and install the Interactive Brokers Trader Workstation (or IB Gateway).

## 2. Download Your Code
Open PowerShell on the new machine and clone your repository:
```powershell
cd C:\
mkdir github
cd github
git clone https://github.com/abhims2012/IBKR.git
cd IBKR
```

## 3. Set Up the Python Environment
Inside the `C:\github\IBKR` folder, create a virtual environment and install the required packages:
```powershell
# Create the virtual environment
python -m venv venv

# Activate it
.\venv\Scripts\activate

# Install the dependencies
pip install -r requirements.txt
```

## 4. Configure IBKR API Settings
You need to make sure the TWS/Gateway on the new machine allows the bot to connect:
1. Open TWS and log in.
2. Go to **File -> Global Configuration -> API -> Settings**.
3. **Check** "Enable ActiveX and Socket Clients".
4. **Uncheck** "Read-Only API" (so the bot can place trades).
5. Ensure the **Socket Port** is `7497` (for paper trading).

## 5. Authenticate Git
Because the bot automatically pushes HTML dashboard updates to GitHub every hour, you need to make sure the new machine is logged into your GitHub account. 
You can trigger the login prompt by doing a manual push first:
```powershell
git push
```
*(A browser window will pop up asking you to sign in to GitHub. Once signed in, your credentials will be saved on the new machine).*

## 6. Start the Bot
That's it! You can now start the bot using your run script:
```powershell
.\run.ps1
```

> **Note**: Since the `trades.json` file is also synced to your GitHub repository, the new workstation will automatically pull your entire trade history when you clone it. The bot will instantly pick up exactly where it left off!
