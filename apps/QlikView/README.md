# Dynamics365 to QlikView
Script used to get `Account` and `Owner` data from Dynamics, convert it to XML and put on shared drive  
```
//ew1-fil-101/Public/_LinuxShareFolder/CRM/SIS/
```
For later use by QlikView report.  
It is runned once a day at `3:00 AM` by jenkins job > http://bma-mte-101:8080/view/Utils/job/Apps/job/dynamics365_2_QlikView
