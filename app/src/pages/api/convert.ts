import type { APIRoute } from 'astro';
import { spawn } from 'child_process';
import { writeFile, unlink, readFile } from 'fs/promises';
import { join } from 'path';
import { tmpdir } from 'os';
import { randomUUID } from 'crypto';

const MAX_FILE_SIZE = 50 * 1024 * 1024; // 50MB
const PYTHON_SCRIPT_PATH = '/Users/hiep/Project/docling-material/src/docling_pdf_simple.py';

export const POST: APIRoute = async ({ request }) => {
  let tempPdfPath: string | null = null;
  let tempMdPath: string | null = null;

  try {
    // Parse the multipart form data
    const formData = await request.formData();
    const pdfFile = formData.get('pdf') as File;

    // Validate file exists
    if (!pdfFile) {
      return new Response(JSON.stringify({ error: 'No PDF file provided' }), {
        status: 400,
        headers: { 'Content-Type': 'application/json' }
      });
    }

    // Validate file type
    if (!pdfFile.type.includes('pdf') && !pdfFile.name.endsWith('.pdf')) {
      return new Response(JSON.stringify({ error: 'Invalid file type. Only PDF files are allowed.' }), {
        status: 400,
        headers: { 'Content-Type': 'application/json' }
      });
    }

    // Validate file size
    if (pdfFile.size > MAX_FILE_SIZE) {
      return new Response(JSON.stringify({ error: 'File size exceeds 50MB limit' }), {
        status: 400,
        headers: { 'Content-Type': 'application/json' }
      });
    }

    // Create temporary file paths
    const uniqueId = randomUUID();
    const originalFileName = pdfFile.name.replace(/\.[^/.]+$/, ''); // Remove extension
    tempPdfPath = join(tmpdir(), `${uniqueId}.pdf`);
    tempMdPath = join(tmpdir(), `${uniqueId}.md`);

    // Convert File to Buffer and save to temp location
    const arrayBuffer = await pdfFile.arrayBuffer();
    const buffer = Buffer.from(arrayBuffer);
    await writeFile(tempPdfPath, buffer);

    console.log(`PDF saved to: ${tempPdfPath}`);
    console.log(`Markdown will be saved to: ${tempMdPath}`);

    // Execute Python script
    const conversionResult = await executePythonScript(tempPdfPath, tempMdPath);

    if (!conversionResult.success) {
      throw new Error(conversionResult.error || 'Python script execution failed');
    }

    // Read the generated markdown file
    const markdownContent = await readFile(tempMdPath, 'utf-8');

    // Clean up temp PDF file (keep MD for now to send response)
    await cleanupFile(tempPdfPath);
    tempPdfPath = null;

    // Return the markdown file as download
    const response = new Response(markdownContent, {
      status: 200,
      headers: {
        'Content-Type': 'text/markdown',
        'Content-Disposition': `attachment; filename="${originalFileName}.md"`,
        'Content-Length': markdownContent.length.toString()
      }
    });

    // Clean up temp markdown file after a short delay to ensure response is sent
    setTimeout(async () => {
      if (tempMdPath) {
        await cleanupFile(tempMdPath);
      }
    }, 1000);

    return response;

  } catch (error) {
    console.error('Error processing PDF:', error);

    // Clean up temp files in case of error
    if (tempPdfPath) await cleanupFile(tempPdfPath);
    if (tempMdPath) await cleanupFile(tempMdPath);

    return new Response(
      JSON.stringify({
        error: error instanceof Error ? error.message : 'An unknown error occurred'
      }),
      {
        status: 500,
        headers: { 'Content-Type': 'application/json' }
      }
    );
  }
};

/**
 * Execute the Python script to convert PDF to Markdown
 */
function executePythonScript(inputPath: string, outputPath: string): Promise<{
  success: boolean;
  error?: string;
  stdout?: string;
}> {
  return new Promise((resolve) => {
    const python = spawn('python3', [
      PYTHON_SCRIPT_PATH,
      '--input', inputPath,
      '--output', outputPath
    ]);

    let stdout = '';
    let stderr = '';

    python.stdout.on('data', (data) => {
      const output = data.toString();
      stdout += output;
      console.log('Python stdout:', output);
    });

    python.stderr.on('data', (data) => {
      const output = data.toString();
      stderr += output;
      console.error('Python stderr:', output);
    });

    python.on('error', (error) => {
      console.error('Failed to start Python process:', error);
      resolve({
        success: false,
        error: `Failed to start Python process: ${error.message}`
      });
    });

    python.on('close', (code) => {
      if (code === 0) {
        console.log('Python script executed successfully');
        resolve({ success: true, stdout });
      } else {
        console.error(`Python script exited with code ${code}`);
        resolve({
          success: false,
          error: stderr || `Python script failed with exit code ${code}`
        });
      }
    });
  });
}

/**
 * Clean up temporary file
 */
async function cleanupFile(filePath: string): Promise<void> {
  try {
    await unlink(filePath);
    console.log(`Cleaned up temp file: ${filePath}`);
  } catch (error) {
    console.error(`Failed to clean up file ${filePath}:`, error);
  }
}
