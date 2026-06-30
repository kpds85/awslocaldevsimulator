# awslocaldevsimulator
Docker compose based local dev environment creator to work with AWS services and postgresql locally. It uses LocalStack to simulate AWS services and provides a simple way to set up a local development environment with a PostgreSQL database. This allows developers to test their applications locally without needing access to actual AWS services and AWS RDS instances.
# ## Usage
1. Clone the repository
2. Provide permission 
```bash
cd awslocaldevsimulator
chmod +x ./install.sh
chmod +x ./uninstall.sh
```
3. Run the install script
```bash
./install.sh
```
4. Inspect / Understand the docker-compose.yml file to see what services are being created and how they are configured. You can modify the configuration as needed for your local development environment.
5. Inspect the sample code in demo.py to see how to interact with the simulated AWS services and PostgreSQL database. You can use the sample code as reference for your own applications.
6. Test run by following the instructions you get from the output of the install script and verify the outputs to ensure local environment is working as expected.
4. Run the uninstall script to remove the environment once you are done with your local development work.
```bash
./uninstall.sh
```