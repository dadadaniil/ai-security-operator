package com.sdc.model.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;
import org.springframework.http.HttpStatus;

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Map;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class GenericResponse<T> {

    private T data;

    @JsonProperty("isSuccess")
    private boolean isSuccess;

    private String message;

    @Builder.Default
    private List<String> errors = new ArrayList<>();

    private int statusCode;

    public static <T> GenericResponse<T> success(HttpStatus statusCode, T data) {
        return GenericResponse.<T>builder()
            .data(data)
            .isSuccess(true)
            .message("Ok")
            .statusCode(statusCode.value())
            .build();
    }

    public static GenericResponse<Void> success(HttpStatus statusCode) {
        return GenericResponse.<Void>builder()
            .isSuccess(true)
            .message("Ok")
            .statusCode(statusCode.value())
            .build();
    }

    public static GenericResponse<Map<String, Long>> successWithId(HttpStatus statusCode, Long id) {
        return GenericResponse.<Map<String, Long>>builder()
            .data(Collections.singletonMap("id", id))
            .isSuccess(true)
            .message("Ok")
            .statusCode(statusCode.value())
            .build();
    }

    public static GenericResponse<Void> error(HttpStatus statusCode, String message, List<String> errors) {
        return GenericResponse.<Void>builder()
            .isSuccess(false)
            .message(message)
            .errors(errors)
            .statusCode(statusCode.value())
            .build();
    }

    public static GenericResponse<Void> error(HttpStatus statusCode, String message, String error) {
        return GenericResponse.<Void>builder()
            .isSuccess(false)
            .message(message)
            .errors(Collections.singletonList(error))
            .statusCode(statusCode.value())
            .build();
    }
}



