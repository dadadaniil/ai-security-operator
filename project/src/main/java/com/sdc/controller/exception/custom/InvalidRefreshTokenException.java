package com.sdc.controller.exception.custom;

public class InvalidRefreshTokenException extends RuntimeException {
    public InvalidRefreshTokenException() {
    }

    @Override
    public String getMessage() {
        return "Refresh token is invalid";
    }
}
