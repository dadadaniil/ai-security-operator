package com.sdc.model.dto;

import com.fasterxml.jackson.annotation.JsonFormat;
import com.sdc.model.EntityValidatorType;
import com.sdc.model.Tag;
import com.sdc.model.TaskType;
import com.sdc.service.annotation.ExistsInDatabase;
import com.sdc.util.Constants;
import jakarta.validation.constraints.*;
import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

import java.math.BigDecimal;
import java.time.OffsetDateTime;
import java.util.List;

@NoArgsConstructor
@AllArgsConstructor
@Getter
@Setter
public class TaskDto {
    @JsonFormat(shape = JsonFormat.Shape.STRING)
    private Long id;

    @NotEmpty(message = "task title must not be empty")
    @Size(min = Constants.MIN_TASK_TITLE, max = Constants.MAX_TASK_TITLE,
        message = "task title must be between " + Constants.MIN_TASK_TITLE + "and " + Constants.MAX_TASK_TITLE + " characters")
    private String title;

    @NotEmpty(message = "task description must not be empty")
    @Size(min = Constants.MINIMAL_DESCRIPTION_TITLE, max = Constants.MAXIMUM_DESCRIPTION_TITLE,
        message = "task description must be between " + Constants.MINIMAL_DESCRIPTION_TITLE +
            " and " + Constants.MAXIMUM_DESCRIPTION_TITLE + " characters")
    private String description;

    @Positive
    private BigDecimal paymentAmount;

    @ExistsInDatabase(entityValidatorType = EntityValidatorType.TAG)
    @NotNull(message = "tags can not be empty")
    private List<Tag> tags;

    private String creatorPublicContacts;

    @ExistsInDatabase(entityValidatorType = EntityValidatorType.CREATOR)
    private UserViewDto creator;

    @ExistsInDatabase(entityValidatorType = EntityValidatorType.CONTRIBUTION)
    @NotNull
    private TaskType type;

    @JsonFormat(shape = JsonFormat.Shape.STRING, pattern = "yyyy-MM-dd'T'HH:mm:ss.SSSX")
    private OffsetDateTime createdAt;

    @JsonFormat(shape = JsonFormat.Shape.STRING, pattern = "yyyy-MM-dd'T'HH:mm:ss.SSSX")
    @NotNull(message = "expected delivery time must not be null")
    @Future(message = "expected delivery time must not be in past")
    private OffsetDateTime deadline;
}
