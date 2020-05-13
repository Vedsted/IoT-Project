CREATE DATABASE FilipsBlue;

USE FilipsBlue;

create table Controllers
(
    id varchar(255) not null
        primary key
);


create table `Groups`
(
    id            varchar(255) not null
        primary key,
    controller_id varchar(255) null,
    constraint Groups_Controllers_id_fk
        foreign key (controller_id) references Controllers (id)
            on update cascade on delete cascade
);


create table Measurements
(
    id          bigint auto_increment
        primary key,
    group_id    varchar(255) not null,
    timestamp   mediumtext   not null,
    lux1        int          not null,
    lux2        int          not null,
    setpoint    int          not null,
    light_red   smallint     not null,
    light_green smallint     not null,
    light_blue  smallint     not null,
    constraint Measurements_Groups_id_fk
        foreign key (group_id) references `Groups` (id)
            on update cascade on delete cascade
);


DROP USER IF EXISTS user;
CREATE USER 'filip'@'%' IDENTIFIED BY 'Chcla15Jonso16';
GRANT USAGE ON *.* TO 'filip'@'%' IDENTIFIED BY 'Chcla15Jonso16';
GRANT ALL privileges ON FilipsBlue.* TO 'filip'@'%';
FLUSH PRIVILEGES;
