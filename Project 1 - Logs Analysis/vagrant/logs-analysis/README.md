## Project 1: Logs Analysis
__________________________________________________

#### Setup Your Environment:
1.	Clone the Udacity-Full-Stack-Web-Developer-Nanodegree repo into your local repository.
2.	[Download the newsdata.sql database](https://d17h27t6h515a5.cloudfront.net/topher/2016/August/57b5f748_newsdata/newsdata.zip) and save into your local repo in the logs-analysis folder of the Project 1 - Logs Analysis folder.
3.	Download [Virtualbox](https://www.virtualbox.org/wiki/Download_Old_Builds_5_1) and [Vagrant](https://www.vagrantup.com/)
4.	(Windows Only) Download Git Bash 
5. Download the [Virtual Machine Configuration](https://github.com/udacity/fullstack-nanodegree-vm)
5.	Run python logs-analysis.py from Git Bash (Windows) or command line (Linux, Mac)
6. 	This will output a text file into your working directory.

#### Generate the Logs Analysis Output
1. Open Git Bash in Windows or Command Prompt with Linux or Mac
2. Go to directory where you cloned the logs-analysis repository.
```
cd <your-local-directory-goes-here/Udacity-Full-Stack-Web-Developer-Nanodegree/Project 1 - Logs Analysis/vagrant/>
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

6. Enter the logs-analysis directory.
```
cd logs-analysis
```

7. Generate the news database
```
psql -d news -f newsdata.sql
```

8. Run logs-analysis Python script.
```
python logs-analysis.py
```

9. logs-analysis-output.txt should appear in your directory!

