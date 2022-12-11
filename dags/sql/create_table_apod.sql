CREATE TABLE IF NOT EXISTS "public"."apod_dev"(
                                        copyright           character varying(256),
                                        "date"              date,
                                        explanation_ptbr    VARCHAR (65535),
                                        hdurl               character varying(256),
                                        media_type          character varying(100),
                                        service_version     character varying(50),
                                        title_ptbr          VARCHAR (1000),
                                        url                 character varying(256),
                                        date_ptbr           character varying(100));