==============================
Azure Training Advance LAB
==============================

Deploy a Python FastAPI web app with PostgreSQL in Azure
=========================================================

:Date: 09/15/2025

Overview
--------

In this tutorial, you deploy a data-driven Python web app (`FastAPI <https://fastapi.tiangolo.com/>`_) to `Azure App Service <https://docs.azure.cn/en-us/app-service/overview>`_ with the `Azure Database for PostgreSQL <https://docs.azure.cn/en-us/postgresql/>`_ relational database service. Azure App Service supports `Python <https://www.python.org/downloads/>`_ in a Linux server environment.

.. image:: https://docs.azure.cn/en-us/app-service/media/tutorial-python-postgresql-app-fastapi/python-postgresql-app-architecture.png
   :alt: Architecture diagram showing an App Service with a PostgreSQL database in Azure
   :align: center

Prerequisites
-------------

To complete this tutorial, you'll need:

• An Azure account with an active subscription. If you don't have an Azure account, you `can create one <https://account.windowsazure.cn/organization/python>`_.
• Knowledge of Python with FastAPI development

Skip to the end
---------------

With `Azure Developer CLI <https://learn.microsoft.com/azure/developer/azure-developer-cli/install-azd>`_ installed, you can skip to the end of the tutorial by running the following commands in an empty working directory:

.. code-block:: bash

    azd auth login
    azd init --template msdocs-fastapi-postgresql-sample-app
    azd up

Sample application
------------------

A sample Python application using FastAPI framework is provided to help you follow along with this tutorial. To deploy it without running it locally, skip this part.

To run the application locally, make sure you have `Python 3.8 or higher <https://www.python.org/downloads/>`_ and `PostgreSQL <https://www.postgresql.org/download/>`_ installed locally. Then, clone the sample repository's ``starter-no-infra`` branch and change to the repository root.

.. code-block:: bash

    git clone -b starter-no-infra https://github.com/Azure-Samples/msdocs-fastapi-postgresql-sample-app
    cd msdocs-fastapi-postgresql-sample-app

Create an .env file as shown below using the .env.sample file as a guide. Set the value of ``DBNAME`` to the name of an existing database in your local PostgreSQL instance. Set the values of ``DBHOST``, ``DBUSER``, and ``DBPASS`` as appropriate for your local PostgreSQL instance.

.. code-block:: bash

    DBNAME=<database name>
    DBHOST=<database-hostname>
    DBUSER=<db-user-name>
    DBPASS=<db-password>

Create a virtual environment for the app:

**Windows:**

.. code-block:: bash

    py -m venv .venv
    .venv\scripts\activate

**macOS/Linux:**

.. code-block:: bash

    python3 -m venv .venv
    source .venv/bin/activate

Install the dependencies:

.. code-block:: bash

    python3 -m pip install -r src/requirements.txt

Install the app as an editable package:

.. code-block:: bash

    python3 -m pip install -e src

Run the sample application with the following commands:

.. code-block:: bash

    # Run database migration
    python3 src/fastapi_app/seed_data.py
    # Run the app at http://127.0.0.1:8000
    python3 -m uvicorn fastapi_app:app --reload --port=8000

1. Create App Service and PostgreSQL
------------------------------------

In this step, you create the Azure resources. The steps used in this tutorial create a set of secure-by-default resources that include App Service and Azure Database for PostgreSQL. For the creation process, you specify:

• The Name for the web app. It's the name used as part of the DNS name for your webapp.
• The Region to run the app physically in the world.
• The Runtime stack for the app. It's where you select the version of Python to use for your app.
• The Hosting plan for the app. It's the pricing tier that includes the set of features and scaling capacity for your app.
• The Resource Group for the app. A resource group lets you group (in a logical container) all the Azure resources needed for the application.

Sign in to the `Azure portal <https://portal.azure.cn/>`_ and follow these steps to create your Azure App Service resources.

Step 1: In the Azure portal:

1. Enter "web app database" in the search bar at the top of the Azure portal.
2. Select the item labeled Web App + Database under the Marketplace heading. You can also navigate to the `creation wizard <https://portal.azure.cn/?feature.customportal=false#create/Microsoft.AppServiceWebAppDatabaseV3>`_ directly.

.. image:: https://docs.azure.cn/en-us/app-service/media/tutorial-python-postgresql-app-fastapi/azure-portal-create-app-postgres-1.png
   :alt: A screenshot showing how to use the search box in the top tool bar to find the Web App + Database creation wizard (FastAPI)
   :align: center

Step 2: In the Create Web App + Database page, fill out the form as follows:

1. Resource Group → Select Create new and use a name of msdocs-python-postgres-tutorial.
2. Region → Any Azure region near you.
3. Name → msdocs-python-postgres-XYZ where XYZ is any three random characters. This name must be unique across Azure.
4. Runtime stack → Python 3.12.
5. Database → PostgreSQL - Flexible Server is selected by default as the database engine. The server name and database name are also set by default to appropriate values.
6. Hosting plan → Basic. When you're ready, you can `scale up <https://docs.azure.cn/en-us/app-service/manage-scale-up>`_ to a production pricing tier later.
7. Select Review + create.
8. After validation completes, select Create.

.. image:: https://docs.azure.cn/en-us/app-service/media/tutorial-python-postgresql-app-fastapi/azure-portal-create-app-postgres-2.png
   :alt: A screenshot showing how to configure a new app and database in the Web App + Database wizard (FastAPI)
   :align: center

Step 3: The deployment takes a few minutes to complete. Once deployment completes, select the Go to resource button. You're taken directly to the App Service app, but the following resources are created:

• Resource group → The container for all the created resources.
• App Service plan → Defines the compute resources for App Service. A Linux plan in the Basic tier is created.
• App Service → Represents your app and runs in the App Service plan.
• Virtual network → Integrated with the App Service app and isolates back-end network traffic.
• Azure Database for PostgreSQL flexible server → Accessible only from within the virtual network. A database and a user are created for you on the server.
• Private DNS zone → Enables DNS resolution of the PostgreSQL server in the virtual network.

.. image:: https://docs.azure.cn/en-us/app-service/media/tutorial-python-postgresql-app-fastapi/azure-portal-create-app-postgres-3.png
   :alt: A screenshot showing the deployment process completed (FastAPI)
   :align: center

Step 4: For FastAPI apps, you must enter a startup command so App service can start your app. On the App Service page:

1. In the left menu, under Settings, select Configuration.
2. In the General settings tab of the Configuration page, enter ``src/entrypoint.sh`` in the Startup Command field under Stack settings.
3. Select Save. When prompted, select Continue. To learn more about app configuration and startup in App Service, see `Configure a Linux Python app for Azure App Service <https://docs.azure.cn/en-us/app-service/configure-language-python>`_.

.. image:: https://docs.azure.cn/en-us/app-service/media/tutorial-python-postgresql-app-fastapi/azure-portal-create-app-postgres-fastapi-4.png
   :alt: A screenshot showing adding a startup command (FastAPI)
   :align: center

2. Verify connection settings
-----------------------------

The creation wizard generated the connectivity variables for you already as `app settings <https://docs.azure.cn/en-us/app-service/configure-common#configure-app-settings>`_. App settings are one way to keep connection secrets out of your code repository. When you're ready to move your secrets to a more secure location, here's an `article on storing in Azure Key Vault <https://docs.azure.cn/en-us/key-vault/certificates/quick-create-python>`_.

Step 1: In the App Service page, in the left menu, select Environment variables.

.. image:: https://docs.azure.cn/en-us/app-service/media/tutorial-python-postgresql-app-fastapi/azure-portal-get-connection-string-fastapi-1.png
   :alt: A screenshot showing how to open the configuration page in App Service (FastAPI)
   :align: center

Step 2: In the App settings tab of the Environment variables page, verify that ``AZURE_POSTGRESQL_CONNECTIONSTRING`` is present. The connection string will be injected into the runtime environment as an environment variable.

.. image:: https://docs.azure.cn/en-us/app-service/media/tutorial-python-postgresql-app-fastapi/azure-portal-get-connection-string-fastapi-2.png
   :alt: A screenshot showing how to see the autogenerated connection string (FastAPI)
   :align: center

3. Deploy sample code
---------------------

In this step, you configure GitHub deployment using GitHub Actions. It's just one of many ways to deploy to App Service, but also a great way to have continuous integration in your deployment process. By default, every ``git push`` to your GitHub repository will kick off the build and deploy action.

Step 1: In a new browser window:

1. Sign in to your GitHub account.
2. Navigate to https://github.com/Azure-Samples/msdocs-fastapi-postgresql-sample-app.
3. Select Fork.
4. Select Create fork.

.. image:: https://docs.azure.cn/en-us/app-service/media/tutorial-python-postgresql-app-fastapi/azure-portal-deploy-sample-code-fastapi-1.png
   :alt: A screenshot showing how to create a fork of the sample GitHub repository (FastAPI)
   :align: center

Step 2: In the GitHub page, open Visual Studio Code in the browser by pressing the ``.`` key.

.. image:: https://docs.azure.cn/en-us/app-service/media/tutorial-python-postgresql-app-fastapi/azure-portal-deploy-sample-code-fastapi-2.png
   :alt: A screenshot showing how to open the Visual Studio Code browser experience in GitHub (FastAPI)
   :align: center

Step 3: In Visual Studio Code in the browser, open src/fastapi/models.py in the explorer. See the environment variables being used in the production environment, including the app settings that you saw in the configuration page.

.. image:: https://docs.azure.cn/en-us/app-service/media/tutorial-python-postgresql-app-fastapi/azure-portal-deploy-sample-code-fastapi-3.png
   :alt: A screenshot showing Visual Studio Code in the browser and an opened file (FastAPI)
   :align: center

Step 4: Back in the App Service page, in the left menu, under Deployment, select Deployment Center.

.. image:: https://docs.azure.cn/en-us/app-service/media/tutorial-python-postgresql-app-fastapi/azure-portal-deploy-sample-code-fastapi-4.png
   :alt: A screenshot showing how to open the deployment center in App Service (FastAPI)
   :align: center

Step 5: In the Deployment Center page:

1. In Source, select GitHub. By default, GitHub Actions is selected as the build provider.
2. Sign in to your GitHub account and follow the prompt to authorize Azure.
3. In Organization, select your account.
4. In Repository, select msdocs-fastapi-postgresql-sample-app.
5. In Branch, select main.
6. Keep the default option selected to Add a workflow.
7. Under Authentication type, select User-assigned identity.
8. In the top menu, select Save. App Service commits a workflow file into the chosen GitHub repository, in the ``.github/workflows`` directory.

.. image:: https://docs.azure.cn/en-us/app-service/media/tutorial-python-postgresql-app-fastapi/azure-portal-deploy-sample-code-fastapi-5.png
   :alt: A screenshot showing how to configure CI/CD using GitHub Actions (FastAPI)
   :align: center

Step 6: In the Deployment Center page:

1. Select Logs. A deployment run is already started.
2. In the log item for the deployment run, select Build/Deploy Logs.

.. image:: https://docs.azure.cn/en-us/app-service/media/tutorial-python-postgresql-app-fastapi/azure-portal-deploy-sample-code-fastapi-6.png
   :alt: A screenshot showing how to open deployment logs in the deployment center (FastAPI)
   :align: center

Step 7: You're taken to your GitHub repository and see that the GitHub action is running. The workflow file defines two separate stages, build and deploy. Wait for the GitHub run to show a status of Complete. It takes about 5 minutes.

.. image:: https://docs.azure.cn/en-us/app-service/media/tutorial-python-postgresql-app-fastapi/azure-portal-deploy-sample-code-fastapi-7.png
   :alt: A screenshot showing a GitHub run in progress (FastAPI)
   :align: center

.. note::
   Having issues? Check the `Troubleshooting guide <https://docs.azure.cn/en-us/app-service/configure-language-python#troubleshooting>`_.

4. Generate database schema
---------------------------

In previous section, you added src/entrypoint.sh as the startup command for your app. entrypoint.sh contains the following line: ``python3 src/fastapi_app/seed_data.py``. This command migrates your database. In the sample app, it only ensures that the correct tables are created in your database. It doesn't populate these tables with any data.

In this section, you'll run this command manually for demonstration purposes. With the PostgreSQL database protected by the virtual network, the easiest way to run the command is in an SSH session with the App Service container.

Step 1: Back in the App Service page, in the left menu:

1. Select SSH.
2. Select Go.

.. image:: https://docs.azure.cn/en-us/app-service/media/tutorial-python-postgresql-app-fastapi/azure-portal-generate-db-schema-fastapi-1.png
   :alt: A screenshot showing how to open the SSH shell for your app from the Azure portal (FastAPI)
   :align: center

Step 2: In the SSH terminal, run ``python3 src/fastapi_app/seed_data.py``. If it succeeds, App Service is connecting successfully to the database. Only changes to files in ``/home`` can persist beyond app restarts. Changes outside of ``/home`` aren't persisted.

.. image:: https://docs.azure.cn/en-us/app-service/media/tutorial-python-postgresql-app-fastapi/azure-portal-generate-db-schema-fastapi-2.png
   :alt: A screenshot showing the commands to run in the SSH shell and their output (FastAPI)
   :align: center

5. Browse to the app
--------------------

Step 1: In the App Service page:

1. From the left menu, select Overview.
2. Select the URL of your app.

.. image:: https://docs.azure.cn/en-us/app-service/media/tutorial-python-postgresql-app-fastapi/azure-portal-browse-app-1.png
   :alt: A screenshot showing how to launch an App Service from the Azure portal (FastAPI)
   :align: center

Step 2: Add a few restaurants to the list. Congratulations, you're running a web app in Azure App Service, with secure connectivity to Azure Database for PostgreSQL.

.. image:: https://docs.azure.cn/en-us/app-service/media/tutorial-python-postgresql-app-fastapi/azure-portal-browse-app-2.png
   :alt: A screenshot of the FastAPI web app with PostgreSQL running in Azure showing restaurants and restaurant reviews (FastAPI)
   :align: center

6. Stream diagnostic logs
-------------------------

The sample app uses the Python Standard Library logging module to help you diagnose issues with your application. The sample app includes calls to the logger as shown in the following code.

.. code-block:: python

    @app.get("/", response_class=HTMLResponse)
    async def index(request: Request, session: Session = Depends(get_db_session)):
        logger.info("root called")
        statement = (
            select(Restaurant, func.avg(Review.rating).label("avg_rating"), func.count(Review.id).label("review_count"))
            .outerjoin(Review, Review.restaurant == Restaurant.id)
            .group_by(Restaurant.id)
        )

Step 1: In the App Service page:

1. From the left menu, under Monitoring, select App Service logs.
2. Under Application logging, select File System.
3. In the top menu, select Save.

.. image:: https://docs.azure.cn/en-us/app-service/media/tutorial-python-postgresql-app-fastapi/azure-portal-stream-diagnostic-logs-1-fastapi.png
   :alt: A screenshot showing how to enable native logs in App Service in the Azure portal
   :align: center

Step 2: From the left menu, select Log stream. You see the logs for your app, including platform logs and logs from inside the container.

.. image:: https://docs.azure.cn/en-us/app-service/media/tutorial-python-postgresql-app-fastapi/azure-portal-stream-diagnostic-logs-2-fastapi.png
   :alt: A screenshot showing how to view the log stream in the Azure portal
   :align: center

.. note::
   Events can take several minutes to show up in the diagnostic logs. Learn more about logging in Python apps in the series on `setting up Azure Monitor for your Python application <https://docs.azure.cn/en-us/azure-monitor/app/opencensus-python>`_.

7. Clean up resources
---------------------

When you're finished, you can delete all of the resources from your Azure subscription by deleting the resource group.

Step 1: In the search bar at the top of the Azure portal:

1. Enter the resource group name.
2. Select the resource group.

.. image:: https://docs.azure.cn/en-us/app-service/media/tutorial-python-postgresql-app-fastapi/azure-portal-clean-up-resources-1.png
   :alt: A screenshot showing how to search for and navigate to a resource group in the Azure portal
   :align: center

Step 2: In the resource group page, select Delete resource group.

.. image:: https://docs.azure.cn/en-us/app-service/media/tutorial-python-postgresql-app-fastapi/azure-portal-clean-up-resources-2.png
   :alt: A screenshot showing the location of the Delete Resource Group button in the Azure portal
   :align: center

Step 3:

1. Enter the resource group name to confirm your deletion.
2. Select Delete.

.. image:: https://docs.azure.cn/en-us/app-service/media/tutorial-python-postgresql-app-fastapi/azure-portal-clean-up-resources-3.png
   :alt: A screenshot of the confirmation dialog for deleting a resource group in the Azure portal
   :align: center

Troubleshooting
---------------

Listed below are issues you might encounter while trying to work through this tutorial and steps to resolve them.

I can't connect to the SSH session
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you can't connect to the SSH session, then the app itself has failed to start. Check the diagnostic logs for details. For example, if you see an error like ``KeyError: 'AZURE_POSTGRESQL_CONNECTIONSTRING'``, it might mean that the environment variable is missing (you might have removed the app setting).

I get an error when running database migrations
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you encounter any errors related to connecting to the database, check if the app settings (``AZURE_POSTGRESQL_CONNECTIONSTRING``) have been changed. Without that connection string, the migrate command can't communicate with the database.

Frequently asked questions
--------------------------

How much does this setup cost?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Pricing for the created resources is as follows:

• The App Service plan is created in Basic tier and can be scaled up or down. See `App Service pricing <https://www.azure.cn/pricing/details/app-service/linux/>`_.
• The PostgreSQL flexible server is created in the lowest burstable tier Standard_B1ms, with the minimum storage size, which can be scaled up or down. See `Azure Database for PostgreSQL pricing <https://www.azure.cn/pricing/details/postgresql/flexible-server/>`_.
• The virtual network doesn't incur a charge unless you configure extra functionality, such as peering. See `Azure Virtual Network pricing <https://www.azure.cn/pricing/details/virtual-network/>`_.
• The private DNS zone incurs a small charge. See `Azure DNS pricing <https://www.azure.cn/pricing/details/dns/>`_.

How do I connect to the PostgreSQL server that's secured behind the virtual network with other tools?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

• For basic access from a command-line tool, you can run ``psql`` from the app's SSH terminal.
• To connect from a desktop tool, your machine must be within the virtual network. For example, it could be an Azure VM that's connected to one of the subnets, or a machine in an on-premises network that has a `site-to-site VPN <https://docs.azure.cn/en-us/vpn-gateway/vpn-gateway-about-vpngateways>`_ connection with the Azure virtual network.
• You can also integrate Azure Cli with the virtual network.

How does local app development work with GitHub Actions?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Using the autogenerated workflow file from App Service as an example, each ``git push`` kicks off a new build and deployment run. From a local clone of the GitHub repository, you make the desired updates and push to GitHub. For example:

.. code-block:: bash

    git add .
    git commit -m "<some-message>"
    git push origin main

8. Configure Azure Active Directory Authentication (Optional)
------------------------------------------------------------

The sample application includes optional Azure Active Directory (AAD) authentication using OpenID Connect (OIDC). This allows users to sign in with their Azure AD accounts for enhanced security and user management.

Features of Azure Authentication
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

• **Azure AD Integration**: Full integration with Azure Active Directory
• **OpenID Connect (OIDC)**: Standards-based authentication flow  
• **Optional Configuration**: Application works with or without Azure AD configured
• **User Profile Management**: Display authenticated user information
• **Session Management**: Secure server-side session storage
• **Automatic Redirects**: Redirect users to login when authentication is required

Step 1: Create Azure AD App Registration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. **Navigate to Azure Portal**
   
   Go to https://portal.azure.com and sign in with your Azure account

2. **Access Azure Active Directory**
   
   Search for "Azure Active Directory" in the search bar and select it

3. **Create App Registration**
   
   • In the left menu, click "App registrations"
   • Click "New registration"
   • Fill out the registration form:
     
     - **Name**: ``FastAPI Restaurant App`` (or your preferred name)
     - **Supported account types**: Choose ``Accounts in this organizational directory only`` (Single tenant)
     - **Redirect URI**: Platform: ``Web``, URI: ``https://your-app-name.azurewebsites.net/auth/callback``

4. **Configure Authentication**
   
   • After creation, go to "Authentication" in the left menu
   • Under "Implicit grant and hybrid flows", ensure:
     
     - ✅ Access tokens (used for implicit flows)
     - ✅ ID tokens (used for implicit and hybrid flows)

5. **Create Client Secret**
   
   • Go to "Certificates & secrets" in the left menu
   • Click "New client secret"
   • Add description: ``FastAPI App Secret``
   • Choose expiration (recommended: 24 months)
   • **Important**: Copy the secret value immediately (it won't be shown again)

6. **Note Important Values**
   
   From the "Overview" page, copy these values:
   
   • **Application (client) ID**: This is your ``AZURE_CLIENT_ID``
   • **Directory (tenant) ID**: This is your ``AZURE_TENANT_ID``
   • **Client Secret**: The secret value you created (this is your ``AZURE_CLIENT_SECRET``)

Step 2: Configure App Service Environment Variables
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In the App Service page, in the left menu, select Environment variables and add the following app settings:

.. code-block:: bash

    AZURE_CLIENT_ID=your-application-client-id
    AZURE_CLIENT_SECRET=your-client-secret
    AZURE_TENANT_ID=your-tenant-id
    AZURE_REDIRECT_URI=https://your-app-name.azurewebsites.net/auth/callback
    SESSION_SECRET_KEY=your-secure-random-session-secret

.. image:: https://docs.azure.cn/en-us/app-service/media/tutorial-python-postgresql-app-fastapi/azure-portal-get-connection-string-fastapi-2.png
   :alt: A screenshot showing how to configure environment variables for Azure authentication
   :align: center

Step 3: Update Application Code (Already Included)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The sample application already includes the Azure authentication code. The key components are:

**Authentication Module** (``src/fastapi_app/auth.py``):

.. code-block:: python

    import msal
    from authlib.integrations.starlette_client import OAuth
    
    class AzureAuth:
        def __init__(self, app_id: str, app_secret: str, tenant_id: str, redirect_uri: str):
            self.authority = f"https://login.microsoftonline.com/{tenant_id}"
            self.msal_app = msal.ConfidentialClientApplication(
                app_id,
                authority=self.authority,
                client_credential=app_secret,
            )

**Authentication Routes** (``src/fastapi_app/app.py``):

.. code-block:: python

    @app.get("/auth/login")
    async def login(request: Request):
        """Initiate Azure AD login"""
        
    @app.get("/auth/callback") 
    async def auth_callback(request: Request, code: str = None):
        """Handle Azure AD callback"""
        
    @app.get("/auth/logout")
    async def logout(request: Request):
        """Logout user"""
        
    @app.get("/auth/profile")
    async def profile(request: Request):
        """Display user profile"""

Step 4: Test Azure Authentication
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. **Deploy the updated application** using GitHub Actions or Azure Developer CLI

2. **Access your application** at ``https://your-app-name.azurewebsites.net``

3. **Test the login flow**:
   
   • Click "Sign in with Azure" in the navigation bar
   • You'll be redirected to Microsoft login page
   • Sign in with your Azure AD account
   • You'll be redirected back to the application
   • Your name should appear in the navigation bar

4. **Verify user profile**:
   
   • Click on your name in the navigation
   • Select "Profile" to view your user information
   • Verify that your Azure AD details are displayed correctly

Authentication Flow Overview
~~~~~~~~~~~~~~~~~~~~~~~~~~~

The authentication process follows the OAuth 2.0/OpenID Connect standard:

1. **Login**: User clicks "Sign in with Azure"
2. **Redirect**: User is redirected to Azure AD login page  
3. **Authentication**: User enters Azure AD credentials
4. **Authorization**: Azure AD redirects back with authorization code
5. **Token Exchange**: Application exchanges code for access token
6. **User Info**: Application fetches user information from Microsoft Graph
7. **Session**: User information is stored in server-side session
8. **Access**: User can now access authenticated features

Security Considerations
~~~~~~~~~~~~~~~~~~~~~~

• **HTTPS Required**: Azure AD requires HTTPS for production redirect URIs
• **Client Secret Security**: Store client secrets securely using Azure Key Vault
• **Session Security**: Use strong, random session secret keys
• **Regular Rotation**: Rotate client secrets regularly
• **State Parameter**: The implementation includes CSRF protection via state parameter

Troubleshooting Authentication Issues
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**"Azure authentication not configured" error**

• Ensure all required environment variables are set in App Service
• Check that values don't contain extra spaces or quotes

**"Invalid redirect URI" error**

• Verify the redirect URI in Azure AD matches exactly what you're using
• Ensure you're using HTTPS for production URLs

**"Failed to get user information" error**

• Check that ``User.Read`` permission is granted in Azure AD
• Ensure the access token is valid and not expired

Optional Configuration
~~~~~~~~~~~~~~~~~~~~~

The Azure authentication is completely optional. If you don't configure the Azure environment variables, the application will run normally without authentication features. This allows for:

• **Development flexibility**: Test without authentication setup
• **Gradual rollout**: Add authentication when ready
• **Multiple environments**: Different auth configurations per environment

Testing Without Azure AD
~~~~~~~~~~~~~~~~~~~~~~~~

To test the application without Azure authentication:

1. Simply don't set the Azure environment variables
2. The application will automatically detect this and disable authentication features
3. All functionality will work normally without user login requirements

User Interface Changes
~~~~~~~~~~~~~~~~~~~~~

When Azure authentication is enabled, users will see:

• **Navigation Bar**: "Sign in with Azure" button when not authenticated
• **User Menu**: User name and profile dropdown when authenticated  
• **Profile Page**: Detailed user information from Azure AD
• **Logout Option**: Clean session termination with Azure AD logout

Next steps
----------

Advance to the next tutorial to learn how to secure your app with a custom domain and certificate.

`Secure with custom domain and certificate <https://docs.azure.cn/en-us/app-service/tutorial-secure-domain-certificate>`_

Learn how App Service runs a Python app:

`Configure Python app <https://docs.azure.cn/en-us/app-service/configure-language-python>`_

Additional Resources
-------------------

• `Azure Active Directory App Registration Guide <https://docs.microsoft.com/en-us/azure/active-directory/develop/quickstart-register-app>`_
• `Microsoft Authentication Library (MSAL) Documentation <https://docs.microsoft.com/en-us/azure/active-directory/develop/msal-overview>`_
• `FastAPI Security Documentation <https://fastapi.tiangolo.com/tutorial/security/>`_
• `OpenID Connect Specification <https://openid.net/connect/>`_