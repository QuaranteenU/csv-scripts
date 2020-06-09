
```sql
SET @row_number = 0; 
UPDATE graduates SET timeslot = FROM_UNIXTIME(30 * (@row_number:=@row_number + 1) + UNIX_TIMESTAMP());
```