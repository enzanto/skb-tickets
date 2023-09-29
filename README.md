# Ticketupdater for SK Brann
This is a simple script to keep track of the sale numbers of SK Brann tickets and display it in a google sheets spreadsheet.

## Prerequisites
For this to work you will need to enable API acces for a google project. [Follow the service account steps](https://docs.gspread.org/en/latest/oauth2.html) and save the credentials on your computer.

You will also need a spreadsheet in google sheet called "matches", either created by the service account or shared to it.

Sheet1 of "matches" should contain a simple table

|kampurl         |       sheet   |   time    |   sheeturl   |  
|----------------|---------------|-----------|--------------|
|url to match    |   sheetname   | time      | url to sheet |

