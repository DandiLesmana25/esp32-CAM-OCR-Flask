<?php
$servername = "localhost"; // Host MySQL
$username = "root";        // Username MySQL
$password = "";    // Password MySQL
$dbname = "ocr_db";        // Nama database

// Koneksi ke database
$conn = new mysqli($servername, $username, $password, $dbname);

// Periksa koneksi
if ($conn->connect_error) {
    die("Connection failed: " . $conn->connect_error);
}

// Mendapatkan data dari POST
$image_name = $_POST['image_name'];
$ocr_text = $_POST['ocr_text'];

// Query untuk menyimpan data
$sql = "INSERT INTO ocr_results (image_name, ocr_text) VALUES ('$image_name', '$ocr_text')";

if ($conn->query($sql) === TRUE) {
    echo json_encode(["message" => "Data saved successfully"]);
} else {
    echo json_encode(["error" => "Error: " . $sql . "<br>" . $conn->error]);
}

// Tutup koneksi
$conn->close();
?>
