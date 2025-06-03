package com.sdc.model.dto;

import com.fasterxml.jackson.annotation.JsonFormat;
import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
public class UserLightDto {
    private String firstName;
    private String lastName;

    @JsonFormat(shape = JsonFormat.Shape.STRING)
    private Long role;
}
