package com.sdc.controller.exception.custom;

public class EmailInUseException extends RuntimeException {
    private final String email;

    private EmailInUseException(String email) {
        this.email = email;
    }

    public static EmailInUseException createWith(String email) {
        return new EmailInUseException(email);
    }

    @Override
    public String getMessage() {
        return "Email '" + email + "' is already in use";
    }
}
