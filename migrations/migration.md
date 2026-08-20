# SQL для ручной миграции

```
ALTER TABLE tracks ADD COLUMN duration VARCHAR;

```

rollback
```
ALTER TABLE tracks DROP COLUMN duration;

```

## users.image: String -> Boolean

Колонка `image` хранила флаг наличия обложки как строку ("True"/NULL), исправлено на `Boolean`.

```
ALTER TABLE users ALTER COLUMN image DROP DEFAULT;
ALTER TABLE users ALTER COLUMN image TYPE boolean USING (image IS NOT NULL AND image <> '');
ALTER TABLE users ALTER COLUMN image SET DEFAULT false;
ALTER TABLE users ALTER COLUMN image SET NOT NULL;
```

rollback
```
ALTER TABLE users ALTER COLUMN image TYPE varchar USING (CASE WHEN image THEN 'True' ELSE NULL END);
ALTER TABLE users ALTER COLUMN image DROP NOT NULL;
ALTER TABLE users ALTER COLUMN image DROP DEFAULT;
```
