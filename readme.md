# Using Apache Iceberg with Apache Spark and Minio - Docker

The proposed solutions for this demo explore how to leverage Apache Iceberg, a data table format, in conjunction with Apache Spark, a distributed processing engine, and Minio, a high-performance object storage solution. The focus is on setting up these components within Docker containers for a controlled and isolated environment. By combining these technologies, you gain efficient data management capabilities, including ACID transactions, schema evolution, and efficient data partitioning within Minio.

## Architecture Overview

### Pipeline Flow Components Overview

#### Theoretical Overview 📖

![Pipeline Flow](https://cdn-images-1.medium.com/max/800/1*gM-qHwR03S6IEh32mgJpjA.gif)

Before diving into the practical implementation, let's have a brief theoretical overview of the technologies we'll be using: Apache Iceberg, Apache Spark, and Minio.

#### Apache Iceberg: A Next-Generation Data Table Format

![Apache Iceberg](https://cdn-images-1.medium.com/max/800/0*S_DICvXdIzlUrVMw.png)

- **Designed for Data Lakes and Warehouses**: Iceberg is specifically built to handle the complexities of large-scale data within data lakes and warehouses. It offers robust data management capabilities while ensuring high performance for analytics workloads.
- **ACID Transactions**: Iceberg supports ACID (Atomicity, Consistency, Isolation, Durability) transactions, guaranteeing data integrity and consistency during writes, even in concurrent write scenarios. This is crucial for maintaining data validity and preventing data corruption, especially when multiple applications or processes are writing to the same data concurrently.
- **Schema Evolution**: Unlike traditional data formats, Iceberg allows you to evolve the schema of your data tables without data loss. This empowers you to adapt your data structure as your analytics requirements or data sources change over time. You can add, remove, or modify columns without rewriting existing data.
- **Time Travel Queries**: Iceberg enables time travel queries, allowing you to access historical data snapshots at any point in time. This is invaluable for auditing changes, debugging analytics pipelines, and performing historical analysis. Iceberg tracks data versions, so you can retrieve a specific version of the table as required.
- **Efficient Partitioning**: Iceberg partitions data tables based on specific columns, optimizing read performance and data management. It stores data files intelligently based on their partition values, allowing Spark to efficiently scan only relevant data for specific queries. This significantly enhances query speed.
- **Data Organization and Compaction**: Iceberg automatically organizes data into efficient file formats like Parquet or ORC, facilitating efficient data compression and columnar access. It also performs data compaction to minimize storage footprint and improve read performance over time.

#### Apache Spark: A Unified Analytics Engine

![Apache Spark](https://cdn-images-1.medium.com/max/800/1*y96i-4yOKWXtX245pzB7jA.png)

- **Large-Scale Data Processing**: Apache Spark is a powerful, open-source distributed processing engine that excels in handling large datasets across clusters of machines. It supports a wide range of data sources, including relational databases, NoSQL databases, CSV files, and object storage like Minio.
- **In-Memory Processing**: Spark leverages in-memory computation for performance gains, keeping frequently accessed data in memory for faster processing compared to traditional disk-based solutions.
- **Structured, Semi-Structured, and Unstructured Data**: Spark can work with a variety of data formats, including structured data (e.g., CSV, JSON), semi-structured data (e.g., XML), and unstructured data (e.g., text). This flexibility makes it ideal for modern data ecosystems that often involve a mix of data types.
- **Machine Learning and Stream Processing**: Beyond traditional analytics, Spark extends to machine learning pipelines and real-time data processing. Spark integrates with popular machine learning libraries like TensorFlow and PyTorch for efficient model training and deployment. It also supports stream processing frameworks like Apache Flink for near real-time data analysis.
- **Seamless Integration with Iceberg**: Spark offers native Iceberg support, allowing you to directly read, write, and query Iceberg tables from your Spark applications. This simplifies data management within your Spark workflows.

#### Minio: A High-Performance Object Storage Server

![Minio](https://cdn-images-1.medium.com/max/800/1*haN-8G7Bwkri3IizPe1WPA.png)

- **Open-Source and Cost-Effective**: Minio is a free and open-source object storage solution, making it a cost-effective alternative to proprietary object storage services offered by major cloud providers. It allows you to manage your own data storage infrastructure and leverage its features within your data lake or warehouse.
- **Scalability and Performance**: Minio is built for scalability. You can easily add more nodes to your Minio cluster as your data storage needs grow, ensuring it can handle increasing data volumes. It also offers good performance characteristics, providing efficient data access for your Spark applications.
- **S3 Compatibility**: Minio is API-compatible with Amazon S3, allowing you to seamlessly integrate it with existing tools and applications that work with S3. This facilitates a smooth transition from traditional cloud object storage to a more cost-effective on-premises solution.
- **Durability and Reliability**: Minio offers data redundancy and replication mechanisms to ensure your data is protected against failures. You can configure data replication across multiple nodes or storage devices, minimizing data loss risks in case of hardware issues.

#### Docker Integration

![Docker Integration](https://cdn-images-1.medium.com/max/800/1*krkTwOsazw1wNQgM1TOjNw.png)

Docker provides a containerization platform that can be used to isolate and manage the execution of these components. Here's how Docker fits into this architecture:
- **Docker Images**: You can create Docker images for each service (Spark Master, Spark Worker, and Minio) containing all the necessary dependencies (Spark, Minio binaries, Iceberg libraries, etc.). This ensures consistent environments and simplifies deployment across different machines.
- **Docker Compose**: A tool like Docker Compose can be used to manage the configuration and deployment of all services together. It defines the services, their dependencies, and environment variables in a single YAML file, streamlining the process of setting up the entire environment.

By leveraging Docker, you can create a portable and isolated development or production environment for working with these technologies.

### Docker Compose Configuration

Below is the Docker Compose file to set up Minio, Spark master, and Spark worker services.

```yaml
version: '3.9'
services:
  minio:
    image: minio/minio
    container_name: minio
    environment:
      MINIO_ACCESS_KEY: minioadmin
      MINIO_SECRET_KEY: minioadmin
    ports:
      - "9000:9000"
      - "9001:9001"
    command: server /data --console-address ":9001"
    volumes:
      - minio_data:/data

  spark-master:
    image: bitnami/spark:latest
    container_name: spark-master-minio-iceberg
    environment:
      - SPARK_MODE=master
      - SPARK_SUBMIT_ARGS=--packages org.apache.iceberg:iceberg-spark3-runtime:0.12.0
    ports:
      - "7077:7077"
      - "8080:8080"

  spark-worker:
    image: bitnami/spark:latest
    container_name: spark-worker-minio-iceberg
    environment:
      - SPARK_MODE=worker
      - SPARK_MASTER_URL=spark://spark-master:7077
      - SPARK_SUBMIT_ARGS=--packages org.apache.iceberg:iceberg-spark3-runtime:0.12.0
    depends_on:
      - spark-master
    ports:
      - "8081:8081"

volumes:
  minio_data:
```

#### Explanation of the Docker Compose File

- **Minio Service**: Runs the Minio server, exposing ports 9000 (API) and 9001 (console). The Minio data is stored in a Docker volume named `minio_data`.
- **Spark Master Service**: Runs the Spark master node with packages for Iceberg. Ports 7077 and 8080 are exposed for Spark UI and master communication.
- **Spark Worker Service**: Runs the Spark worker node, connected to the Spark master. It also includes packages for Iceberg.

### Build Image

By running the following command:

```sh
docker-compose up -d
```

You will see that all services are up or if there is any issue it will be raised (hope you will not face any problem 😄).

![Docker Desktop](https://cdn-images-1.medium.com/max/800/1*AAyzdxhA3b6zTOUPQpbn1A.png)
![Docker Command Line](https://cdn-images-1.medium.com/max/800/1*CghiZduOwnj864SUx_bP9A.png)

First, check is to visit [http://localhost:9001/browser](http://localhost:9001/browser) and see if you have the below image:

![Minio Service](https://cdn-images-1.medium.com/max/800/1*GupVjmXsedM-BouZG9kMyg.png)

Minio service is up 😉. After all services are up, let's move to create a simple data pipeline with read and write from Apache Iceberg using Apache Spark and Minio, for that please check the exisited python code in **./src** folder
c

## Summary

This setup allows you to efficiently manage and process large-scale data with Spark and Iceberg, while using Minio for scalable object storage