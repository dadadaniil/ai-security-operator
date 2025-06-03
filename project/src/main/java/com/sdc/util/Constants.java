package com.sdc.util;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;

@Component
public final class Constants {
    public Integer tokenValidHours;
    public String timeZone;
    public static final int TOKEN_PREFIX_LENGTH = 7;
    public static final String DEFAULT_TASK_PAGE_NUMBER = "0";
    public static final String DEFAULT_TASK_PAGE_SIZE = "10";
    public static final String DEFAULT_TYPE_PAGE_SIZE = "10";
    public static final String DEFAULT_TAG_PAGE_SIZE = "50";
    public static final int MIN_TASK_TITLE = 10;
    public static final int MAX_TASK_TITLE = 100;
    public static final int MINIMAL_DESCRIPTION_TITLE = 10;
    public static final int MAXIMUM_DESCRIPTION_TITLE = 5000;
    public static final int MINIMAL_PASSWORD_LENGTH = 6;
    public static final int MAXIMUM_PASSWORD_LENGTH = 32;

    public Constants(
        @Value("${application.token_valid_hours}") Integer tokenValidHours,
        @Value("${application.timezone}") String timeZone
    ) {
        this.tokenValidHours = tokenValidHours;
        this.timeZone = timeZone;
    }
}
