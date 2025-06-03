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
import jakarta.validation.ConstraintValidatorContext;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.mockito.junit.jupiter.MockitoSettings;
import org.mockito.quality.Strictness;

import java.util.Collections;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.anyString;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

@ExtendWith(MockitoExtension.class)
@MockitoSettings(strictness = Strictness.LENIENT)
class ExistsInDatabaseValidatorTest {
    @Mock
    private TagRepository tagRepository;

    @Mock
    private UserRepository userRepository;

    @Mock
    private TaskTypeRepository taskTypeRepository;

    @Mock
    private TaskRepository taskRepository;

    @InjectMocks
    private ExistsInDatabaseValidator validator;

    @DisplayName("Test for ExistsInDatabase() validator for tags")
    @Test
    void testIsValidTag() {
        Tag tag = new Tag();
        tag.setId(1L);
        ExistsInDatabase existsInDatabase = mock(ExistsInDatabase.class);
        when(existsInDatabase.entityValidatorType()).thenReturn(EntityValidatorType.TAG);
        validator.initialize(existsInDatabase);

        ConstraintValidatorContext context = mock(ConstraintValidatorContext.class);
        ConstraintValidatorContext.ConstraintViolationBuilder violationBuilder = mock(
            ConstraintValidatorContext.ConstraintViolationBuilder.class);
        when(context.buildConstraintViolationWithTemplate(anyString())).thenReturn(violationBuilder);
        when(violationBuilder.addConstraintViolation()).thenReturn(context);
        when(tagRepository.findAllById(Collections.singletonList(tag.getId()))).thenReturn(
            Collections.singletonList(tag));

        assertTrue(validator.isValid(Collections.singletonList(tag), context));
    }

    @DisplayName("Negative test for ExistsInDatabase() validator for tags")
    @Test
    void TestIsValidTagNegative() {
        Tag tag = new Tag();
        tag.setId(1L);
        ExistsInDatabase existsInDatabase = mock(ExistsInDatabase.class);
        when(existsInDatabase.entityValidatorType()).thenReturn(EntityValidatorType.TAG);
        validator.initialize(existsInDatabase);

        when(tagRepository.existsById(tag.getId())).thenReturn(false);

        ConstraintValidatorContext context = mock(ConstraintValidatorContext.class);
        ConstraintValidatorContext.ConstraintViolationBuilder violationBuilder = mock(
            ConstraintValidatorContext.ConstraintViolationBuilder.class);
        when(context.buildConstraintViolationWithTemplate(anyString())).thenReturn(violationBuilder);
        when(violationBuilder.addConstraintViolation()).thenReturn(context);

        assertFalse(validator.isValid(Collections.singletonList(tag), context));
    }

    @DisplayName("Test for ExistsInDatabase() validator for creator")
    @Test
    void testCreatorValidatorExists() {
        UserViewDto userViewDto = new UserViewDto();
        userViewDto.setId(1L);
        ExistsInDatabase existsInDatabase = mock(ExistsInDatabase.class);

        ConstraintValidatorContext context = mock(ConstraintValidatorContext.class);
        when(userRepository.existsById(userViewDto.getId())).thenReturn(true);
        when(existsInDatabase.entityValidatorType()).thenReturn(EntityValidatorType.CREATOR);

        validator.initialize(existsInDatabase);
        assertTrue(validator.isValid(userViewDto, context));
    }

    @DisplayName("Negative test for ExistsInDatabase() validator for creator")
    @Test
    void testCreatorValidatorExistsNegative() {
        UserViewDto userViewDto = new UserViewDto();
        userViewDto.setId(1L);
        ExistsInDatabase existsInDatabase = mock(ExistsInDatabase.class);

        ConstraintValidatorContext context = mock(ConstraintValidatorContext.class);
        ConstraintValidatorContext.ConstraintViolationBuilder violationBuilder = mock(
            ConstraintValidatorContext.ConstraintViolationBuilder.class);
        when(existsInDatabase.entityValidatorType()).thenReturn(EntityValidatorType.CREATOR);
        when(userRepository.existsById(userViewDto.getId())).thenReturn(false);
        when(context.buildConstraintViolationWithTemplate(anyString())).thenReturn(violationBuilder);
        when(violationBuilder.addConstraintViolation()).thenReturn(context);

        validator.initialize(existsInDatabase);
        assertFalse(validator.isValid(userViewDto, context));
    }

    @DisplayName("Test for ExistsInDatabase() validator for contribution")
    @Test
    void testContributionValidator() {
        TaskType contribution = new TaskType();
        contribution.setId(1L);
        ExistsInDatabase existsInDatabase = mock(ExistsInDatabase.class);

        when(taskTypeRepository.existsById(contribution.getId())).thenReturn(true);
        when(existsInDatabase.entityValidatorType()).thenReturn(EntityValidatorType.CONTRIBUTION);
        ConstraintValidatorContext context = mock(ConstraintValidatorContext.class);

        validator.initialize(existsInDatabase);
        assertTrue(validator.isValid(contribution, context));
    }

    @DisplayName("Negative test for ExistsInDatabase() validator for contribution")
    @Test
    void testContributionValidatorNegative() {
        TaskType contribution = new TaskType();
        contribution.setId(1L);
        ExistsInDatabase existsInDatabase = mock(ExistsInDatabase.class);

        ConstraintValidatorContext context = mock(ConstraintValidatorContext.class);
        ConstraintValidatorContext.ConstraintViolationBuilder violationBuilder = mock(
            ConstraintValidatorContext.ConstraintViolationBuilder.class);
        when(taskTypeRepository.existsById(contribution.getId())).thenReturn(false);
        when(existsInDatabase.entityValidatorType()).thenReturn(EntityValidatorType.CONTRIBUTION);
        when(context.buildConstraintViolationWithTemplate(anyString())).thenReturn(violationBuilder);
        when(violationBuilder.addConstraintViolation()).thenReturn(context);

        validator.initialize(existsInDatabase);
        assertFalse(validator.isValid(contribution, context));
    }

    @DisplayName("Test for taskValidator()")
    @Test
    void testTaskValidatorExists() {
        Long taskId = 1L;
        when(taskRepository.existsById(taskId)).thenReturn(true);

        assertTrue(validator.taskValidator(taskId));
    }

    @DisplayName("Negative test for taskValidator() when task does not exist")
    @Test
    void testTaskValidatorDoesNotExist() {
        Long taskId = 1L;
        when(taskRepository.existsById(taskId)).thenReturn(false);

        assertThrows(EntityNotFoundException.class, () -> validator.taskValidator(taskId));
    }
}