sqlcmd -S EW1-SQL-102 -E -Q "PRINT Suser_Sname();"
sqlcmd -S EW1-SQL-102 -E -Q "exec [ErpJvs001].[dbo].q_hl_crm_CreateUpdateAccountsCRM '161650'"

