package com.sdc.service.annotation.validator;

import com.sdc.model.EntityValidatorType;
import com.sdc.model.Tag;
import com.sdc.model.TaskType;
import com.sdc.model.dto.UserViewDto;
import com.sdc.repository.TagRepository;
import com.sdc.repository.TaskRepository;
import com.sdc.repository.TaskTypeRepository;
import com.sdc.repository.UserRepository;
import com.sdc.service.annotation.ExistsInDatabase;
import jakarta.persistence.EntityNotFoundException;
import jakarta.validation.ConstraintValidator;
import jakarta.validation.ConstraintValidatorContext;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Component;

import java.util.List;
import java.util.stream.Collectors;

/**
 * Validator class for checking if an entity exists in the database.
 * This class implements the ConstraintValidator interface and is used in conjunction with the ExistsInDatabase annotation.
 * It supports validation for Tag, User, and TypeOfContribution entities.
 *
 * @see com.sdc.service.annotation.ExistsInDatabase
 * @see jakarta.validation.ConstraintValidator
 */

@Component
public class ExistsInDatabaseValidator implements ConstraintValidator<ExistsInDatabase, Object> {
    private final TagRepository tagRepository;

    private final UserRepository userRepository;

    private final TaskTypeRepository taskTypeRepository;

    private final TaskRepository taskRepository;


    private EntityValidatorType entityValidatorType;

    public ExistsInDatabaseValidator(TagRepository tagRepository, UserRepository userRepository, TaskTypeRepository taskTypeRepository, TaskRepository taskRepository) {
        this.tagRepository = tagRepository;
        this.userRepository = userRepository;
        this.taskTypeRepository = taskTypeRepository;
        this.taskRepository = taskRepository;
    }

    /**
     * Initializes the validator with the specified entity type.
     *
     * @param constraintAnnotation the ExistsInDatabase annotation that this validator is linked to
     */
    @Override
    public void initialize(ExistsInDatabase constraintAnnotation) {
        this.entityValidatorType = constraintAnnotation.entityValidatorType();
    }

    /**
     * Validates the specified value.
     * The validation logic differs depending on the entity type.
     *
     * @param value   the object to validate
     * @param context the context in which the constraint is evaluated
     * @return true if the value passes the constraint, false otherwise
     */
    @Override
    public boolean isValid(Object value, ConstraintValidatorContext context) {
        return switch (entityValidatorType) {
            case TAG -> tagValidator((List<Tag>) value, context);
            case CREATOR -> creatorValidator((UserViewDto) value, context);
            case CONTRIBUTION -> contributionValidator((TaskType) value, context);
        };
    }

    /**
     * Validates a TypeOfContribution entity.
     *
     * @param value   the TypeOfContribution to validate
     * @param context the context in which the constraint is evaluated
     * @return true if the TypeOfContribution exists in the database, false otherwise
     */
    private boolean contributionValidator(TaskType value, ConstraintValidatorContext context) {
        if (!taskTypeRepository.existsById(value.getId())) {
            context.disableDefaultConstraintViolation();
            context.buildConstraintViolationWithTemplate("Contribution with id " + value.getId() + " does not exist")
                .addConstraintViolation();
            return false;
        }
        return true;
    }

    /**
     * Validates a User entity.
     *
     * @param value   the User to validate
     * @param context the context in which the constraint is evaluated
     * @return true if the User exists in the database, false otherwise
     */
    private boolean creatorValidator(UserViewDto value, ConstraintValidatorContext context) {
        if (!userRepository.existsById(value.getId())) {
            context.disableDefaultConstraintViolation();
            context.buildConstraintViolationWithTemplate("User with id " + value.getId() + " does not exist")
                .addConstraintViolation();
            return false;
        }
        return true;
    }

    /**
     * Validates a list of Tag entities.
     *
     * @param value   the list of Tags to validate
     * @param context the context in which the constraint is evaluated
     * @return true if all Tags in the list exist in the database, false otherwise
     */
    private boolean tagValidator(List<Tag> value, ConstraintValidatorContext context) {
        List<Long> tagIds = value.stream()
            .map(Tag::getId)
            .collect(Collectors.toList());

        List<Long> existingTagIds = tagRepository.findAllById(tagIds).stream()
            .map(Tag::getId)
            .toList();

        for (Long id : tagIds) {
            if (!existingTagIds.contains(id)) {
                context.disableDefaultConstraintViolation();
                context.buildConstraintViolationWithTemplate("Tag with id " + id + " does not exist")
                    .addConstraintViolation();
                return false;
            }
        }
        return true;
    }

    public boolean taskValidator(Long id) {
        if (!taskRepository.existsById(id)) {
            throw new EntityNotFoundException("Task with id " + id + " does not exist");
        }
        return true;
    }
}
