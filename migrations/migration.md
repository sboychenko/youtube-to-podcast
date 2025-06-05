# SQL для ручной миграции

```
ALTER TABLE tracks ADD COLUMN duration VARCHAR;

```

rollback
```
ALTER TABLE tracks DROP COLUMN duration;

```
