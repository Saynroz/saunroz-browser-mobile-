cmake_minimum_required(VERSION 3.22.1)
project("saynroz")

add_library(saynroz SHARED
    saynroz.cpp
    saynroz_jni.cpp
)

find_library(log-lib log)
target_link_libraries(saynroz ${log-lib})