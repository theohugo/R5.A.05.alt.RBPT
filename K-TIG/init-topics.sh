#!/bin/bash
kafka-topics.sh --create --topic enter_arena_topic --bootstrap-server kafka:9092 --partitions 3 --replication-factor 1
sleep 2
kafka-topics.sh --create --topic gold_topic --bootstrap-server kafka:9092 --partitions 3 --replication-factor 1
sleep 2
kafka-topics.sh --create --topic set_action_topic --bootstrap-server kafka:9092 --partitions 3 --replication-factor 1
sleep 2
kafka-topics.sh --create --topic damage_topic --bootstrap-server kafka:9092 --partitions 3 --replication-factor 1
sleep 2
kafka-topics.sh --create --topic death_topic --bootstrap-server kafka:9092 --partitions 3 --replication-factor 1
