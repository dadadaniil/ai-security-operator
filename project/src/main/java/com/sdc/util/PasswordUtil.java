package com.sdc.util;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Component;

@Component
public class PasswordUtil {

    private final PasswordEncoder encoder;

    @Autowired
    public PasswordUtil(PasswordEncoder encoder) {
        this.encoder = encoder;
    }

    /**
     * Encodes the provided password using BCrypt hashing algorithm.
     *
     * @param password the plain text password to be encoded
     * @return the encoded password
     */
    public String hashPassword(String password) {
        return encoder.encode(password);
    }

    /**
     * Checks if the provided password matches the encoded password.
     *
     * @param password        the plain text password to check
     * @param encodedPassword the encoded password to compare with
     * @return true if the password matches the encoded password, false otherwise
     */
    public boolean isEqual(String password, String encodedPassword) {
        return encoder.matches(password, encodedPassword);
    }
}