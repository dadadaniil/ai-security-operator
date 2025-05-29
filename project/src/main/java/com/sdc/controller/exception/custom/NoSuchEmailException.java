package com.sdc.controller.exception.custom;

public class NoSuchEmailException extends RuntimeException {
    private final String email;

    private NoSuchEmailException(String email) {
        this.email = email;
    }

    public static NoSuchEmailException createWith(String email) {
        return new NoSuchEmailException(email);
    }

    @Override
    public String getMessage() {
        return "User with email '" + email + "' does not exist";
    }
}
