java
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

public class VectorStoreTest {

    @Test
    public void testGetDocuments() {
        // Arrange
        VectorStore vectorStore = new VectorStore();
        String file_id = "12345";
        String[] ids = {"1", "2", "3"};
        vectorStore.addDocument(file_id, ids);

        // Act
        boolean result = vectorStore.get(where={"file_id": file_id});

        // Assert
        assertTrue(result);
    }

    @Test
    public void testGetDocumentsNoDocuments() {
        // Arrange
        VectorStore vectorStore = new VectorStore();
        String file_id = "12345";

        // Act
        boolean result = vectorStore.get(where={"file_id": file_id});

        // Assert
        assertFalse(result);
    }

    @Test
    public void testGetDocumentsError() {
        // Arrange
        VectorStore vectorStore = new VectorStore();
        String file_id = "12345";

        // Act and Assert
        boolean result = vectorStore.get(where={"file_id": file_id});
        assertTrue(result);
    }

    @Test
    public void testConvertListToStr() {
        // Arrange
        VectorStore vectorStore = new VectorStore();
        String file_id = "12345";
        String[] ids = {"1", "2", "3"};
        vectorStore.addDocument(file_id, ids);

        // Act
        boolean result = vectorStore.get(where={"file_id": file_id});

        // Assert
        assertEquals("['1', '2', '3']", result);
    }

    @Test
    public void testConvertListToStrEmpty() {
        // Arrange
        VectorStore vectorStore = new VectorStore();
        String file_id = "12345";
        String[] ids = {};

        // Act
        boolean result = vectorStore.get(where={"file_id": file_id});

        // Assert
        assertEquals("", result);
    }

    @Test
    public void testConvertListToStrSingleElement() {
        // Arrange
        VectorStore vectorStore = new VectorStore();
        String file_id = "12345";
        String[] ids = {"1"};

        // Act
        boolean result = vectorStore.get(where={"file_id": file_id});

        // Assert
        assertEquals("['1']", result);
    }

    @Test
    public void testConvertListToStrMultipleElements() {
        // Arrange
        VectorStore vectorStore = new VectorStore();
        String file_id = "12345";
        String[] ids = {"1", "2", "3"};

        // Act
        boolean result = vectorStore.get(where={"file_id": file_id});

        // Assert
        assertEquals("[\"1\", \"2\", \"3\"]", result);
    }

    @Test
    public void testConvertListToStrNonStringElements() {
        // Arrange
        VectorStore vectorStore = new VectorStore();
        String file_id = "12345";
        String[] ids = {"1", 2, "3"};

        // Act and Assert
        boolean result = vectorStore.get(where={"file_id": file_id});
        assertEquals("[\"1\", 2, \"3\"]", result);
    }

    @Test
    public void testConvertListToStrNonListElements() {
        // Arrange
        VectorStore vectorStore = new VectorStore();
        String file_id = "12345";
        String[] ids = {"1", "a"};

        // Act and Assert
        boolean result = vectorStore.get(where={"file_id": file_id});
        assertEquals("[\"1\", \"a\"]", result);
    }

    @Test
    public void testConvertListToStrNestedLists() {
        // Arrange
        VectorStore vectorStore = new VectorStore();
        String file_id = "12345";
        String[] ids = {"[1, 2]", "[3, 4]"};

        // Act and Assert
        boolean result = vectorStore.get(where={"file_id": file_id});
        assertEquals("[\"[1, 2\"]\", \"[3, 4\"]\"]", result);
    }

    @Test
    public void testConvertListToStrNestedListsEmpty() {
        // Arrange
        VectorStore vectorStore = new VectorStore();
        String file_id = "12345";
        String[] ids = "{}";

        // Act and Assert
        boolean result = vectorStore.get(where={"file_id": file_id});
        assertEquals("{}", result);
    }

    @Test
    public void testConvertListToStrNestedListsSingleElement() {
        // Arrange
        VectorStore vectorStore = new VectorStore();
        String file_id = "12345";
        String[] ids = "[\"[1, 2\"]\"]";

        // Act and Assert
        boolean result = vectorStore.get(where={"file_id": file_id});
        assertEquals("[\"[1, 2\"]\"]", result);
    }

    @Test
    public void testConvertListToStrNestedListsMultipleElements() {
        // Arrange
        VectorStore vectorStore = new VectorStore();
        String file_id = "12345";
        String[] ids = "[\"[1, 2\"]\", \"[3, 4\"]\"]";

        // Act and Assert
        boolean result = vectorStore.get(where={"file_id": file_id});
        assertEquals("[\"[1, 2\"]\", \"[3, 4\"]\"]", result);
    }

    @Test
    public void testConvertListToStrNestedListsNonStringElements() {
        // Arrange
        VectorStore vectorStore = new VectorStore();
        String file_id = "12345";
        String[] ids = "[\"[1, 2\"]\", [3, 4]]";

        // Act and Assert
        boolean result = vectorStore.get(where={"file_id": file_id});
        assertEquals("[\"[1, 2\"]\", [3, 4]]", result);
    }

    @Test
    public void testConvertListToStrNestedListsNonListElements() {
        // Arrange
        VectorStore vectorStore = new VectorStore();
        String file_id = "12345";
        String[] ids = "[\"[1, 2\"]\", \"a\"]";

        // Act and Assert
        boolean result = vectorStore.get(where={"file_id": file_id});
        assertEquals("[\"[1, 2\"]\", \"a\"]", result);
    }

    @Test
    public void testConvertListToStrNestedListsNonStringAndNonListElements() {
        // Arrange
        VectorStore vectorStore = new VectorStore();
        String file_id = "12345";
        String[] ids = "[\"[1, 2\"]\", \"a\", [3, 4]]";

        // Act and Assert
        boolean result = vectorStore.get(where={"file_id": file_id});
        assertEquals("[\"[1, 2\"]\", \"a\", [3, 4]]", result);
    }
}
