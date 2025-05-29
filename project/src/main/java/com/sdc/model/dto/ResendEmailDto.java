package com.sdc.model.dto;

import com.fasterxml.jackson.annotation.JsonFormat;
import jakarta.validation.constraints.Positive;
import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
public class ResendEmailDto {

    @Positive(message = "userId must not be empty")
    @JsonFormat(shape = JsonFormat.Shape.STRING)
    private Long userId;
}
