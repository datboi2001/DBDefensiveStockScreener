# DBDefensiveStockScreener
A tremendously faster version of DefensiveStockScreener.
You have to create your own database before you can use the application. Another thing that you have to do is collect API keys from Finnhub.
This is a better version of DefensiveStockScreener.
This screener connects to a PostgreSQL stock database.
Once you filled out the path and the name of the report, you will be directed to a screen where you can enter your own criteria.
If any criteria is left blank or does not follow the instruction that is coming up ahead, you will have to enter it again.
If there are any criteria that you don't want to use, fill it as Any, else you have to fill it with a comparison operator (<, <=, >=, >, =) followed by a space followed by the value of the criteria.
Once that is done, the result will be written to the path you specified and you will be prompted to try again. If nothing is found, you will be prompted to use the path you choose earlier and start again.

Update: The project has some database issues, meaning I don't have the budget to host a database so I will release the source code for the project.
