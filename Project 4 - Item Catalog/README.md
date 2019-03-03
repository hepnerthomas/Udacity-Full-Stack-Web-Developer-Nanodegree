## Project 4: Financial Assets Application
__________________________________________________


The Financial Assets Application shows a list of Asset Classes. Users can login to the application via Facebook to view existing Asset Classes and create new ones. Financial Assets are contained within each Asset Class and can be created, edited, or deleted by authenticated users.

#### Setup Your Environment:
1.	Clone the Udacity-Full-Stack-Web-Developer-Nanodegree repo into your local repository.
2.	Download [Virtualbox](https://www.virtualbox.org/wiki/Download_Old_Builds_5_1) and [Vagrant](https://www.vagrantup.com/)
3.	(Windows Only) Download Git Bash 
4.  Download the [Virtual Machine Configuration](https://github.com/udacity/fullstack-nanodegree-vm)
5.	Follow the steps below to run the application on your localhost.
6.  Access the Financial Asset Application in your Chrome Web Browser.

#### Steps to Run Application:
1. Open Git Bash in Windows or Command Prompt with Linux or Mac
2. Go to directory where you cloned the **Project 4 - Item Catalog** repository.
```
cd <your-local-directory-goes-here/Udacity-Full-Stack-Web-Developer-Nanodegree/Project 4 - Item Catalog/vagrant/>
```

3. Start the Vagrant VM.
```
vagrant up
```

4. Connect to the Vagrant VM.
```
vagrant ssh
```
5. Enter the vagrant directory.
```
cd /vagrant
```


6. Enter the catalog directory.
```
cd catalog
```

7. Compile Python code to create the database for the application.
```
python database_setup.py
```

8. Generate the database with default Asset Classes and Financial Assets.
```
python seed_database.py
```

9. Run "python project.py" to run the application on port 8000. 
```
python project.py
```

10. Open a Chrome Web Browser. 

11. Visit http://localhost:8000/asset_classes/ or http://localhost:8000/ to view the application in the browser.
