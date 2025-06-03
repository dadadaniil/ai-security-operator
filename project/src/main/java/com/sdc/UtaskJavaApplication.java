package com.sdc;

import com.sdc.util.Constants;
import jakarta.annotation.PostConstruct;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.scheduling.annotation.EnableScheduling;

import java.util.TimeZone;

@SpringBootApplication
@EnableScheduling
public class UtaskJavaApplication {

    private final Constants constants;

    @Autowired
    public UtaskJavaApplication(Constants constants) {
        this.constants = constants;
    }

    public static void main(String[] args) {
        SpringApplication.run(UtaskJavaApplication.class, args);
    }

    @PostConstruct
    public void init() {
        // Setting Spring Boot SetTimeZone
        TimeZone.setDefault(TimeZone.getTimeZone(constants.timeZone));
    }
}
