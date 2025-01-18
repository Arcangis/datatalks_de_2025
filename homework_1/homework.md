# Module 1 Homework: Docker & SQL

In this homework we'll prepare the environment and practice
Docker and SQL

When submitting your homework, you will also need to include
a link to your GitHub repository or other public code-hosting
site.

This repository should contain the code for solving the homework. 

When your solution has SQL or shell commands and not code
(e.g. python files) file format, include them directly in
the README file of your repository.


## Question 1. Understanding docker first run 

Run docker with the `python:3.12.8` image in an interactive mode, use the entrypoint `bash`.

What's the version of `pip` in the image?

- <b>24.3.1</b>
- 24.2.1
- 23.3.1
- 23.2.1

Dockerfile:
```Dockerfile
FROM python:3.12.8
ENTRYPOINT ["/bin/bash"]
```
Bash:
```bash
docker build -t python:3.12.8 . 
docker run -it python:3.12.8
pip --version
pip 24.3.1 from /usr/local/lib/python3.12/site-packages/pip (python 3.12)
```

## Question 2. Understanding Docker networking and docker-compose

Given the following `docker-compose.yaml`, what is the `hostname` and `port` that **pgadmin** should use to connect to the postgres database?

```yaml
services:
  db:
    container_name: postgres
    image: postgres:17-alpine
    environment:
      POSTGRES_USER: 'postgres'
      POSTGRES_PASSWORD: 'postgres'
      POSTGRES_DB: 'ny_taxi'
    ports:
      - '5433:5432'
    volumes:
      - vol-pgdata:/var/lib/postgresql/data

  pgadmin:
    container_name: pgadmin
    image: dpage/pgadmin4:latest
    environment:
      PGADMIN_DEFAULT_EMAIL: "pgadmin@pgadmin.com"
      PGADMIN_DEFAULT_PASSWORD: "pgadmin"
    ports:
      - "8080:80"
    volumes:
      - vol-pgadmin_data:/var/lib/pgadmin  

volumes:
  vol-pgdata:
    name: vol-pgdata
  vol-pgadmin_data:
    name: vol-pgadmin_data
```

- postgres:5433
- localhost:5432
- db:5433
- postgres:5432
- <b>db:5432</b>

Based on: [docker-compose network documentation](https://docs.docker.com/compose/how-tos/networking/)
- A container is created using db's configuration. It joins the network under the name db.
-  Networked service-to-service communication uses the CONTAINER_PORT.

##  Prepare Postgres

Run Postgres and load data as shown in the videos
We'll use the green taxi trips from October 2019:

```bash
wget https://github.com/DataTalksClub/nyc-tlc-data/releases/download/green/green_tripdata_2019-10.csv.gz
```

You will also need the dataset with zones:

```bash
wget https://github.com/DataTalksClub/nyc-tlc-data/releases/download/misc/taxi_zone_lookup.csv
```

Download this data and put it into Postgres.

You can use the code from the course. It's up to you whether
you want to use Jupyter or a python script.

```bash
docker build -t ingestion:v1
```

- Trip Data:
```bash
docker run -it \
    --network=homework_1_default \
      ingestion:v1 \
    --user=postgres \
    --password=postgres \
    --host=db \
    --port=5432 \
    --db=ny_taxi \
    --table_name=green_tripdata \
    --url="https://github.com/DataTalksClub/nyc-tlc-data/releases/download/green/green_tripdata_2019-10.csv.gz" \
    --date_cols="['lpep_pickup_datetime', 'lpep_dropoff_datetime']"
```

- Trip Zone:
```bash
docker run -it \
    --network=homework_1_default \
      ingestion:v1 \
    --user=postgres \
    --password=postgres \
    --host=db \
    --port=5432 \
    --db=ny_taxi \
    --table_name=trip_zone \
    --url="https://github.com/DataTalksClub/nyc-tlc-data/releases/download/misc/taxi_zone_lookup.csv"
```

## Question 3. Trip Segmentation Count

During the period of October 1st 2019 (inclusive) and November 1st 2019 (exclusive), how many trips, **respectively**, happened:
1. Up to 1 mile
2. In between 1 (exclusive) and 3 miles (inclusive),
3. In between 3 (exclusive) and 7 miles (inclusive),
4. In between 7 (exclusive) and 10 miles (inclusive),
5. Over 10 miles 

Answers:

- 104,802;  197,670;  110,612;  27,831;  35,281
- <b>104,802;  198,924;  109,603;  27,678;  35,189</b>
- 104,793;  201,407;  110,612;  27,831;  35,281
- 104,793;  202,661;  109,603;  27,678;  35,189
- 104,838;  199,013;  109,645;  27,688;  35,202

SQL:
```sql
SELECT COUNT(1),
	CASE 
		WHEN trip_distance <= 1
			THEN 1
		WHEN trip_distance > 1 AND trip_distance <= 3
			THEN 2
		WHEN trip_distance > 3 AND trip_distance <= 7
			THEN 3
		WHEN trip_distance > 7 AND trip_distance <= 10
			THEN 4
		WHEN trip_distance > 10
			THEN 5
	END AS milliage_class
FROM public.green_tripdata
WHERE lpep_pickup_datetime BETWEEN '2019-10-01 00:00:00' AND '2019-10-31 23:59:59' AND
lpep_dropoff_datetime BETWEEN '2019-10-01 00:00:00' AND '2019-10-31 23:59:59'
GROUP BY milliage_class
```

## Question 4. Longest trip for each day

Which was the pick up day with the longest trip distance?
Use the pick up time for your calculations.

Tip: For every day, we only care about one single trip with the longest distance. 

- 2019-10-11
- 2019-10-24
- 2019-10-26
- <b>2019-10-31</b>

SQL:
```sql
SELECT MAX(trip_distance), lpep_pickup_datetime
FROM public.green_tripdata
GROUP BY trip_distance, lpep_pickup_datetime
ORDER BY trip_distance DESC
```

## Question 5. Three biggest pickup zones

Which were the top pickup locations with over 13,000 in
`total_amount` (across all trips) for 2019-10-18?

Consider only `lpep_pickup_datetime` when filtering by date.
 
- <b>East Harlem North, East Harlem South, Morningside Heights</b>
- East Harlem North, Morningside Heights
- Morningside Heights, Astoria Park, East Harlem South
- Bedford, East Harlem North, Astoria Park

SQL:
```sql
SELECT zn."Zone", SUM(tp.total_amount) as total_zone_amount
FROM public.green_tripdata AS tp 
LEFT JOIN  public.trip_zone AS zn
	ON tp."PULocationID" = zn."LocationID"
WHERE tp.lpep_pickup_datetime BETWEEN '2019-10-18 00:00:00' AND '2019-10-18 23:59:59'
GROUP BY zn."Zone"
HAVING SUM(tp.total_amount) > 13000
ORDER BY total_zone_amount DESC
```

## Question 6. Largest tip

For the passengers picked up in October 2019 in the zone
name "East Harlem North" which was the drop off zone that had
the largest tip?

Note: it's `tip` , not `trip`

We need the name of the zone, not the ID.

- Yorkville West
- <b>JFK Airport</b>
- East Harlem North
- East Harlem South

SQL:
```sql
WITH temp_table (tip_amount, "DOLocationID")
AS (
	SELECT tp.tip_amount, tp."DOLocationID"
	FROM public.green_tripdata AS tp 
	LEFT JOIN  public.trip_zone AS zn
		ON tp."PULocationID" = zn."LocationID"
	WHERE tp.lpep_pickup_datetime BETWEEN '2019-10-01 00:00:00' AND '2019-10-31 23:59:59'
	AND zn."Zone" = 'East Harlem North'
)
SELECT MAX(tp.tip_amount), zn."Zone"
FROM temp_table AS tp 
LEFT JOIN  public.trip_zone AS zn
	ON tp."DOLocationID" = zn."LocationID"
GROUP BY tp.tip_amount, zn."Zone"
ORDER BY tp.tip_amount DESC
```

## Terraform

In this section homework we'll prepare the environment by creating resources in GCP with Terraform.

In your VM on GCP/Laptop/GitHub Codespace install Terraform. 
Copy the files from the course repo
[here](../../../01-docker-terraform/1_terraform_gcp/terraform) to your VM/Laptop/GitHub Codespace.

Modify the files as necessary to create a GCP Bucket and Big Query Dataset.

Bash:
```bash
terraform init
terraform plan -var-file=vars.tfvars
terraform apply -var-file=vars.tfvars
terraform destroy -var-file=vars.tfvars
```
## Question 7. Terraform Workflow

Which of the following sequences, **respectively**, describes the workflow for: 
1. Downloading the provider plugins and setting up backend,
2. Generating proposed changes and auto-executing the plan
3. Remove all resources managed by terraform`

Answers:
- terraform import, terraform apply -y, terraform destroy
- teraform init, terraform plan -auto-apply, terraform rm
- terraform init, terraform run -auto-approve, terraform destroy
- <b>terraform init, terraform apply -auto-approve, terraform destroy</b>
- terraform import, terraform apply -y, terraform rm


## Submitting the solutions

* Form for submitting: https://courses.datatalks.club/de-zoomcamp-2025/homework/hw1
