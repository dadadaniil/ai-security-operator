package com.sdc.service.util;

import com.sdc.util.PasswordUtil;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;

import static org.junit.jupiter.api.Assertions.*;

public class PasswordUtilTest {

    private PasswordUtil passwordUtil;

    @BeforeEach
    public void beforeEach() {
        passwordUtil = new PasswordUtil(new BCryptPasswordEncoder());
    }

    @Test
    public void testGenerateSalt() {
        String salt = passwordUtil.hashPassword("password");
        assertNotNull(salt);
    }

    @Test
    public void testIsExpectedPassword() {
        String hashedPassword = passwordUtil.hashPassword("19847ghjcfg29834jhfiwsdeufh29384723498287hf");
        boolean isExpectedPassword = passwordUtil.isEqual("19847ghjcfg29834jhfiwsdeufh29384723498287hf", hashedPassword);
        assertTrue(isExpectedPassword);
    }

    @Test
    public void testIsExpectedPasswordNegative() {
        String hashedPassword = passwordUtil.hashPassword("password");
        boolean isExpectedPassword = passwordUtil.isEqual("#^ksdfhfds892L", hashedPassword);
        assertFalse(isExpectedPassword);
    }

}