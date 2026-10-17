--
-- PostgreSQL database dump
--

\restrict IXMSWcgMWfp1ehsx9jlGQgBDoZr8Dmtgo9sBt4cLWcqCHCZRVye9LOeOUhce9N7

-- Dumped from database version 18.6
-- Dumped by pg_dump version 18.6

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: files; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.files (
    file_id bigint NOT NULL,
    file_name character varying(255) NOT NULL,
    file_path text NOT NULL,
    file_extension character varying(20),
    file_size bigint DEFAULT 0 NOT NULL,
    last_modified timestamp without time zone,
    last_scanned timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);


ALTER TABLE public.files OWNER TO postgres;

--
-- Name: files_file_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

ALTER TABLE public.files ALTER COLUMN file_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.files_file_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: files files_file_path_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.files
    ADD CONSTRAINT files_file_path_key UNIQUE (file_path);


--
-- Name: files files_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.files
    ADD CONSTRAINT files_pkey PRIMARY KEY (file_id);


--
-- PostgreSQL database dump complete
--

\unrestrict IXMSWcgMWfp1ehsx9jlGQgBDoZr8Dmtgo9sBt4cLWcqCHCZRVye9LOeOUhce9N7
