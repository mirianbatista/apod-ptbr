CREATE TABLE IF NOT EXISTS "public"."apod_teste_dag_hook"(
                                        copyright           character varying(256),
                                        "date"              date,
                                        explanation         VARCHAR (65535),
                                        hdurl               character varying(256),
                                        media_type          character varying(100),
                                        service_version     character varying(50),
                                        title               character varying(256),
                                        url                 character varying(256),
                                        processed_timestamp timestamp without time zone);