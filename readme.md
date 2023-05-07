## How to run

To run the app, you should create a Docker container using the following command:

```sh
docker run -d \
--name server \
-e POSTGRES_USER=sirius_2023 \
-e POSTGRES_PASSWORD=change_me \
-e PGDATA=/postgres_data_inside_container \
-v ~/Your/db/path/postgres_data:/postgres_data_inside_container \
-p 38746:5432 \
postgres:15.1
```

You should also log into the database and add your own login and password. Here is an example:

```sql
CREATE EXTENSION "uuid-ossp";

CREATE TABLE IF NOT EXISTS equipment(
    id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    model text not null,
    manufacturer text not null,
    year_of_issue int not null,
    service_cost int not null,
    electricity_cost int not null
);
```
You should create a telegram bot using @botfather in telegram and paste token of created bot into a row in main.py:
```
bot = telebot.TeleBot("PASTE_HERE")
```
Finally, you can run the app using following command:
```
python main.py
```