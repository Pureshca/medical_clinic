--
-- PostgreSQL database dump
--

\restrict mpAof9eZZtDHs6wrv57cF0KxCFwj5Kq82h5zEqifnySCZ0MH9ODCOi7r5prbRBT

-- Dumped from database version 15.14 (Debian 15.14-1.pgdg13+1)
-- Dumped by pg_dump version 15.14 (Debian 15.14-1.pgdg13+1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
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
-- Name: admins; Type: TABLE; Schema: public; Owner: medical_user
--

CREATE TABLE public.admins (
    id integer NOT NULL,
    login character varying(50) NOT NULL,
    password_hash character varying(255) NOT NULL,
    created_at timestamp without time zone
);


ALTER TABLE public.admins OWNER TO medical_user;

--
-- Name: admins_id_seq; Type: SEQUENCE; Schema: public; Owner: medical_user
--

CREATE SEQUENCE public.admins_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.admins_id_seq OWNER TO medical_user;

--
-- Name: admins_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: medical_user
--

ALTER SEQUENCE public.admins_id_seq OWNED BY public.admins.id;


--
-- Name: doctors; Type: TABLE; Schema: public; Owner: medical_user
--

CREATE TABLE public.doctors (
    id integer NOT NULL,
    first_name character varying(50) NOT NULL,
    last_name character varying(50) NOT NULL,
    "position" character varying(100) NOT NULL,
    login character varying(50) NOT NULL,
    password_hash character varying(255) NOT NULL,
    created_at timestamp without time zone
);


ALTER TABLE public.doctors OWNER TO medical_user;

--
-- Name: doctors_id_seq; Type: SEQUENCE; Schema: public; Owner: medical_user
--

CREATE SEQUENCE public.doctors_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.doctors_id_seq OWNER TO medical_user;

--
-- Name: doctors_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: medical_user
--

ALTER SEQUENCE public.doctors_id_seq OWNED BY public.doctors.id;


--
-- Name: medicines; Type: TABLE; Schema: public; Owner: medical_user
--

CREATE TABLE public.medicines (
    id integer NOT NULL,
    name character varying(100) NOT NULL,
    description text,
    side_effects text,
    usage_method text,
    created_at timestamp without time zone
);


ALTER TABLE public.medicines OWNER TO medical_user;

--
-- Name: medicines_id_seq; Type: SEQUENCE; Schema: public; Owner: medical_user
--

CREATE SEQUENCE public.medicines_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.medicines_id_seq OWNER TO medical_user;

--
-- Name: medicines_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: medical_user
--

ALTER SEQUENCE public.medicines_id_seq OWNED BY public.medicines.id;


--
-- Name: patients; Type: TABLE; Schema: public; Owner: medical_user
--

CREATE TABLE public.patients (
    id integer NOT NULL,
    first_name character varying(50) NOT NULL,
    last_name character varying(50) NOT NULL,
    gender character varying(10) NOT NULL,
    date_of_birth date NOT NULL,
    address text,
    login character varying(50) NOT NULL,
    password_hash character varying(255) NOT NULL,
    created_at timestamp without time zone
);


ALTER TABLE public.patients OWNER TO medical_user;

--
-- Name: patients_id_seq; Type: SEQUENCE; Schema: public; Owner: medical_user
--

CREATE SEQUENCE public.patients_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.patients_id_seq OWNER TO medical_user;

--
-- Name: patients_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: medical_user
--

ALTER SEQUENCE public.patients_id_seq OWNED BY public.patients.id;


--
-- Name: visit_medicines; Type: TABLE; Schema: public; Owner: medical_user
--

CREATE TABLE public.visit_medicines (
    id integer NOT NULL,
    visit_id integer NOT NULL,
    medicine_id integer NOT NULL,
    doctor_instructions text,
    created_at timestamp without time zone
);


ALTER TABLE public.visit_medicines OWNER TO medical_user;

--
-- Name: visit_medicines_id_seq; Type: SEQUENCE; Schema: public; Owner: medical_user
--

CREATE SEQUENCE public.visit_medicines_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.visit_medicines_id_seq OWNER TO medical_user;

--
-- Name: visit_medicines_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: medical_user
--

ALTER SEQUENCE public.visit_medicines_id_seq OWNED BY public.visit_medicines.id;


--
-- Name: visits; Type: TABLE; Schema: public; Owner: medical_user
--

CREATE TABLE public.visits (
    id integer NOT NULL,
    patient_id integer NOT NULL,
    doctor_id integer NOT NULL,
    date timestamp without time zone NOT NULL,
    location character varying(100),
    symptoms text,
    diagnosis text,
    prescriptions text,
    created_at timestamp without time zone
);


ALTER TABLE public.visits OWNER TO medical_user;

--
-- Name: visits_id_seq; Type: SEQUENCE; Schema: public; Owner: medical_user
--

CREATE SEQUENCE public.visits_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.visits_id_seq OWNER TO medical_user;

--
-- Name: visits_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: medical_user
--

ALTER SEQUENCE public.visits_id_seq OWNED BY public.visits.id;


--
-- Name: admins id; Type: DEFAULT; Schema: public; Owner: medical_user
--

ALTER TABLE ONLY public.admins ALTER COLUMN id SET DEFAULT nextval('public.admins_id_seq'::regclass);


--
-- Name: doctors id; Type: DEFAULT; Schema: public; Owner: medical_user
--

ALTER TABLE ONLY public.doctors ALTER COLUMN id SET DEFAULT nextval('public.doctors_id_seq'::regclass);


--
-- Name: medicines id; Type: DEFAULT; Schema: public; Owner: medical_user
--

ALTER TABLE ONLY public.medicines ALTER COLUMN id SET DEFAULT nextval('public.medicines_id_seq'::regclass);


--
-- Name: patients id; Type: DEFAULT; Schema: public; Owner: medical_user
--

ALTER TABLE ONLY public.patients ALTER COLUMN id SET DEFAULT nextval('public.patients_id_seq'::regclass);


--
-- Name: visit_medicines id; Type: DEFAULT; Schema: public; Owner: medical_user
--

ALTER TABLE ONLY public.visit_medicines ALTER COLUMN id SET DEFAULT nextval('public.visit_medicines_id_seq'::regclass);


--
-- Name: visits id; Type: DEFAULT; Schema: public; Owner: medical_user
--

ALTER TABLE ONLY public.visits ALTER COLUMN id SET DEFAULT nextval('public.visits_id_seq'::regclass);


--
-- Name: admins admins_login_key; Type: CONSTRAINT; Schema: public; Owner: medical_user
--

ALTER TABLE ONLY public.admins
    ADD CONSTRAINT admins_login_key UNIQUE (login);


--
-- Name: admins admins_pkey; Type: CONSTRAINT; Schema: public; Owner: medical_user
--

ALTER TABLE ONLY public.admins
    ADD CONSTRAINT admins_pkey PRIMARY KEY (id);


--
-- Name: doctors doctors_login_key; Type: CONSTRAINT; Schema: public; Owner: medical_user
--

ALTER TABLE ONLY public.doctors
    ADD CONSTRAINT doctors_login_key UNIQUE (login);


--
-- Name: doctors doctors_pkey; Type: CONSTRAINT; Schema: public; Owner: medical_user
--

ALTER TABLE ONLY public.doctors
    ADD CONSTRAINT doctors_pkey PRIMARY KEY (id);


--
-- Name: medicines medicines_name_key; Type: CONSTRAINT; Schema: public; Owner: medical_user
--

ALTER TABLE ONLY public.medicines
    ADD CONSTRAINT medicines_name_key UNIQUE (name);


--
-- Name: medicines medicines_pkey; Type: CONSTRAINT; Schema: public; Owner: medical_user
--

ALTER TABLE ONLY public.medicines
    ADD CONSTRAINT medicines_pkey PRIMARY KEY (id);


--
-- Name: patients patients_login_key; Type: CONSTRAINT; Schema: public; Owner: medical_user
--

ALTER TABLE ONLY public.patients
    ADD CONSTRAINT patients_login_key UNIQUE (login);


--
-- Name: patients patients_pkey; Type: CONSTRAINT; Schema: public; Owner: medical_user
--

ALTER TABLE ONLY public.patients
    ADD CONSTRAINT patients_pkey PRIMARY KEY (id);


--
-- Name: visit_medicines unique_visit_medicine; Type: CONSTRAINT; Schema: public; Owner: medical_user
--

ALTER TABLE ONLY public.visit_medicines
    ADD CONSTRAINT unique_visit_medicine UNIQUE (visit_id, medicine_id);


--
-- Name: visit_medicines visit_medicines_pkey; Type: CONSTRAINT; Schema: public; Owner: medical_user
--

ALTER TABLE ONLY public.visit_medicines
    ADD CONSTRAINT visit_medicines_pkey PRIMARY KEY (id);


--
-- Name: visits visits_pkey; Type: CONSTRAINT; Schema: public; Owner: medical_user
--

ALTER TABLE ONLY public.visits
    ADD CONSTRAINT visits_pkey PRIMARY KEY (id);


--
-- Name: visit_medicines visit_medicines_medicine_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: medical_user
--

ALTER TABLE ONLY public.visit_medicines
    ADD CONSTRAINT visit_medicines_medicine_id_fkey FOREIGN KEY (medicine_id) REFERENCES public.medicines(id) ON DELETE CASCADE;


--
-- Name: visit_medicines visit_medicines_visit_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: medical_user
--

ALTER TABLE ONLY public.visit_medicines
    ADD CONSTRAINT visit_medicines_visit_id_fkey FOREIGN KEY (visit_id) REFERENCES public.visits(id) ON DELETE CASCADE;


--
-- Name: visits visits_doctor_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: medical_user
--

ALTER TABLE ONLY public.visits
    ADD CONSTRAINT visits_doctor_id_fkey FOREIGN KEY (doctor_id) REFERENCES public.doctors(id) ON DELETE CASCADE;


--
-- Name: visits visits_patient_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: medical_user
--

ALTER TABLE ONLY public.visits
    ADD CONSTRAINT visits_patient_id_fkey FOREIGN KEY (patient_id) REFERENCES public.patients(id) ON DELETE CASCADE;


--
-- PostgreSQL database dump complete
--

\unrestrict mpAof9eZZtDHs6wrv57cF0KxCFwj5Kq82h5zEqifnySCZ0MH9ODCOi7r5prbRBT

