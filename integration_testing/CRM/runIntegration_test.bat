sqlcmd -S EW1-SQL-716 -E -Q "PRINT Suser_Sname();"
sqlcmd -S EW1-SQL-716 -E -Q "exec [ErpTst005].[dbo].q_hl_crm_CreateUpdateAccountsCRM '987654321'"

