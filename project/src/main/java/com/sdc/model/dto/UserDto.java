package com.sdc.model.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import jakarta.validation.constraints.Email;
import jakarta.validation.constraints.NotEmpty;
import jakarta.validation.constraints.Positive;
import jakarta.validation.constraints.Size;
import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

import static com.sdc.util.Constants.MAXIMUM_PASSWORD_LENGTH;
import static com.sdc.util.Constants.MINIMAL_PASSWORD_LENGTH;

@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor

public class UserDto {
    @NotEmpty(message = "first name must not be empty")
    private String firstName;

    @NotEmpty(message = "last name must not be empty")
    private String lastName;

    @Size(min = MINIMAL_PASSWORD_LENGTH, max = MAXIMUM_PASSWORD_LENGTH,
        message = "password size should be between " + MINIMAL_PASSWORD_LENGTH +
            " and " + MAXIMUM_PASSWORD_LENGTH + " characters")
    @NotEmpty(message = "password must not be empty")
    private String password;

    @NotEmpty(message = "email must not be empty")
    @Email
    private String email;

    @JsonProperty("role")
    @Positive(message = "roleId must be greater than 0")
    private Long roleId;
}
