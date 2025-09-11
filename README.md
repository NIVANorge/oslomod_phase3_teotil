# OsloMod Phase 3: TEOTIL3 modelling

TEOTIL3 modelling for Phase 3 of the OsloMod project.

## Running the Streamlit

The app is designed to help with sense-checking the scenarios. It is not very refined!

### Option 1: From JupyterHub

 1. Open a terminal on the JupyterHub and `cd` into the `oslomod_phase3_teotil` directory
    
 2. Run `streamlit run ./app/main.py`

 3. Open a new browser tab and navigate to https://hub.p.niva.no/hub/user-redirect/proxy/8501/

### Option 2: Docker

 1. Clone the repository and build the Dockerfile with ` docker build -t oslomod_scenarios .`
    
 2. Start the container with `docker run -p 8501:8501 oslomod_scenarios`

 3. Open a new tab and navigate to http://localhost:8501
