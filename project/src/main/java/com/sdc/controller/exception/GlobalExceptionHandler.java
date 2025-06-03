package com.sdc.controller.exception;

import com.sdc.controller.exception.custom.*;
import com.sdc.model.dto.GenericResponse;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.bind.annotation.ControllerAdvice;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.context.request.WebRequest;

import java.time.OffsetDateTime;
import java.util.Collections;
import java.util.List;
import java.util.Objects;

@ControllerAdvice
public class GlobalExceptionHandler {
    private static final Logger logger = LoggerFactory.getLogger(GlobalExceptionHandler.class);

    @ExceptionHandler({
        InvalidTokenException.class,
        TooOftenRequestedException.class,
        EmailAlreadyVerifiedException.class,
        NoSuchUserIdException.class
    })
    public ResponseEntity<GenericResponse<Void>> badRequestExceptionHandler(RuntimeException ex, WebRequest request) {
        return exceptionHandleHelper(ex, request, HttpStatus.BAD_REQUEST);
    }

    @ExceptionHandler(MethodArgumentNotValidException.class)
    public ResponseEntity<GenericResponse<Void>> handleValidationException(MethodArgumentNotValidException ex, WebRequest request) {
        HttpStatus status = HttpStatus.BAD_REQUEST;
        String errorMessage = Objects.requireNonNull(ex.getBindingResult().getFieldError()).getDefaultMessage();

        String formattedErrorMessage = wrapMessage(
            status.value(),
            ex.getBindingResult().getFieldError().getDefaultMessage(),
            request
        );
        List<String> errors = Collections.singletonList(formattedErrorMessage);

        GenericResponse<Void> result = GenericResponse.error(status, errorMessage, errors);
        logError(ex, errorMessage);
        return new ResponseEntity<>(result, status);
    }

    @ExceptionHandler({NoSuchEmailException.class, UnverifiedUserException.class})
    public ResponseEntity<GenericResponse<Void>> unauthorizedExceptionHandler(RuntimeException ex, WebRequest request) {
        return exceptionHandleHelper(ex, request, HttpStatus.UNAUTHORIZED);
    }

    @ExceptionHandler({ExpiredTokenException.class, InvalidRefreshTokenException.class})
    public ResponseEntity<GenericResponse<Void>> forbiddenExceptionHandler(RuntimeException ex, WebRequest request) {
        return exceptionHandleHelper(ex, request, HttpStatus.FORBIDDEN);
    }

    @ExceptionHandler({EmailInUseException.class})
    public ResponseEntity<GenericResponse<Void>> conflictExceptionHandler(RuntimeException ex, WebRequest request) {
        return exceptionHandleHelper(ex, request, HttpStatus.CONFLICT);
    }

    @ExceptionHandler(Exception.class)
    public ResponseEntity<GenericResponse<Void>> globalExceptionHandler(Exception ex, WebRequest request) {
        return exceptionHandleHelper(ex, request, HttpStatus.INTERNAL_SERVER_ERROR);
    }

    private ResponseEntity<GenericResponse<Void>> exceptionHandleHelper(Exception ex, WebRequest request, HttpStatus status) {
        String message = wrapMessage(status.value(), ex, request);
        logError(ex, ex.getMessage());
        return new ResponseEntity<>(GenericResponse.error(status, ex.getMessage(), message), status);
    }

    private void logError(Exception ex, String reason) {
        logger.error("Handling {}, due to {}", ex.getClass().getSimpleName(), reason);
    }

    private static String wrapMessage(int statusCode, Exception exception, WebRequest request) {
        return wrapMessage(statusCode, exception.getMessage(), request);
    }

    private static String wrapMessage(int statusCode, String exceptionMessage, WebRequest request) {
        return " " + statusCode +
            ", at: " + OffsetDateTime.now() +
            ", " + exceptionMessage +
            ", " + request.getDescription(false);
    }
}