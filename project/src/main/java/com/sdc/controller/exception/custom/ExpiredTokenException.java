package com.sdc.controller.exception.custom;

public class ExpiredTokenException extends RuntimeException {
    private final String token;

    private ExpiredTokenException(String token) {
        this.token = token;
    }

    public static ExpiredTokenException createWith(String token) {
        return new ExpiredTokenException(token);
    }

    @Override
    public String getMessage() {
        return "Confirmation token '" + token + "' has expired";
    }
}
