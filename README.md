# DBDefensiveStockScreener
A tremendously faster version of DefensiveStockScreener, one where there's no need to collect an API key

This is a better version of DefensiveStockScreener. There's no need to collect API keys in order to run the screener anymore.
This screener connects to a PostgreSQL stock database that I maintained and updated everyday.
Once you filled out the path and the name for the result, you will be directed to a screen where you can enter your own criteria.
If any criteria is left blank or does not follow the instruction that is coming up ahead, you will have to enter it again.
If there are any criteria that you don't want to use, fill it as Any, else you have to fill it with a comparison operator (<, <=, >=, >, =) followed by a space followed by the value of the criteria.
Once that is done, the result will be written to the path you specified and you will be prompted to try again. If nothing is found, you will be prompted to use the path you choose earlier and start again.

Third-party libraries used in the project: pandas, psycopg2, easygui, openpyxl

Don't try to run run.py cause it does not have all of the dependencies. I left out one for security reason.
A working prototype is available in dist. Its name is run.exe.
Written in Python 3.8.1
