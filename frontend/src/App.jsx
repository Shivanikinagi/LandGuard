import { motion } from "framer-motion";
import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { 
  Shield, 
  Zap, 
  Lock, 
  Globe, 
  FileText, 
  Brain, 
  Database, 
  Link,
  Github,
  Download,
  Terminal,
  Upload,
  Eye,
  FileArchive
} from "lucide-react";

export default function LandGuardLanding() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [password, setPassword] = useState("");
  const [processing, setProcessing] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const features = [
    {
      icon: <Brain className="w-8 h-8" />,
      title: "AI Fraud Detection",
      description: "Advanced machine learning algorithms detect anomalies and suspicious patterns in land documents."
    },
    {
      icon: <Lock className="w-8 h-8" />,
      title: "Military-Grade Encryption",
      description: "AES-256-GCM encryption with PBKDF2 key derivation ensures your documents are secure."
    },
    {
      icon: <Zap className="w-8 h-8" />,
      title: "Intelligent Compression",
      description: "Proprietary compression algorithms reduce file sizes while preserving document integrity."
    },
    {
      icon: <Globe className="w-8 h-8" />,
      title: "Decentralized Storage",
      description: "IPFS integration provides permanent, tamper-proof storage for your important documents."
    },
    {
      icon: <Link className="w-8 h-8" />,
      title: "Blockchain Verification",
      description: "Immutable audit trails on Polygon blockchain ensure document authenticity."
    },
    {
      icon: <FileText className="w-8 h-8" />,
      title: "Secure Packaging",
      description: "Custom .ppc container format with rich metadata for comprehensive document management."
    }
  ];

  const stats = [
    { value: "256-bit", label: "AES Encryption" },
    { value: "<1s", label: "Processing Time" },
    { value: "99.9%", label: "Uptime" },
    { value: "10M+", label: "Documents Secured" }
  ];

  const steps = [
    {
      title: "Document Upload",
      description: "Upload your land documents for processing"
    },
    {
      title: "Fraud Detection",
      description: "AI analyzes documents for anomalies and risks"
    },
    {
      title: "Secure Compression",
      description: "Documents are compressed and encrypted"
    },
    {
      title: "Blockchain Storage",
      description: "Files stored on IPFS with blockchain verification"
    },
    {
      title: "Audit Trail",
      description: "Complete tamper-proof record generated"
    }
  ];

  const handleFileChange = (event) => {
    setSelectedFile(event.target.files[0]);
    setError(null);
    setResult(null);
  };

  const handleCompress = async () => {
    console.log("Compress button clicked", selectedFile);
    if (!selectedFile) {
      setError("Please select a file first");
      return;
    }

    setProcessing(true);
    setError(null);
    setResult(null);

    try {
      const formData = new FormData();
      formData.append('file', selectedFile);
      formData.append('password', password || 'default_password');

      console.log("Sending compress request...");
      const response = await fetch('http://localhost:8000/api/documents/compress', {
        method: 'POST',
        body: formData,
      });
      console.log("Response received:", response.status);

      if (response.ok) {
        // Handle file download
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = selectedFile.name + '.ppc';
        document.body.appendChild(a);
        a.click();
        a.remove();
        window.URL.revokeObjectURL(url);

        setResult({
          type: "success",
          message: "File compressed and downloaded successfully!",
          details: {
            action: "compress",
            filename: selectedFile.name + '.ppc',
            size: blob.size
          }
        });
      } else {
        const errorData = await response.json();
        setError(errorData.error || "Compression failed");
      }
    } catch (err) {
      console.error("Compression error:", err);
      setError("Network error: " + err.message + ". Make sure API server is running on port 8000.");
    } finally {
      setProcessing(false);
    }
  };
  const handleProcess = async () => {
    console.log("Process with LandGuard button clicked");
    
    if (!selectedFile) {
      setError("Please select a file first");
      return;
    }

    setProcessing(true);
    setError(null);
    setResult(null);

    try {
      const formData = new FormData();
      formData.append('file', selectedFile);
      formData.append('password', password || 'default_password');

      const response = await fetch('http://localhost:8000/api/documents/process', {
        method: 'POST',
        body: formData,
      });

      if (response.ok) {
        const data = await response.json();
        setResult({
          type: "success",
          message: data.message || "Document processed successfully through LandGuard!",
          data: data
        });
      } else {
        const errorData = await response.json();
        setError(errorData.error || "Processing failed");
      }
    } catch (err) {
      console.error("Processing error:", err);
      setError("Network error: " + err.message + ". Please check if the API server is running.");
    } finally {
      setProcessing(false);
    }
  };

  const handleDecompress = async () => {
    if (!selectedFile) {
      setError("Please select a .ppc file first");
      return;
    }

    // Check if file is a .ppc file
    if (!selectedFile.name.endsWith('.ppc')) {
      setError("Please select a .ppc file for decompression");
      return;
    }

    setProcessing(true);
    setError(null);
    setResult(null);

    try {
      const formData = new FormData();
      formData.append('file', selectedFile);
      formData.append('password', password || 'default_password');

      const response = await fetch('http://localhost:8000/api/documents/decompress', {
        method: 'POST',
        body: formData,
      });

      if (response.ok) {
        const data = await response.json();
        setResult({
          type: "success",
          message: data.message || "File decompressed successfully!",
          details: {
            action: "decompress",
            originalFilename: data.original_filename,
            outputPath: data.output_path
          }
        });
      } else {
        const errorData = await response.json();
        setError(errorData.error || "Decompression failed");
      }
    } catch (err) {
      console.error("Decompression error:", err);
      setError("Network error: " + err.message + ". Please check if the API server is running.");
    } finally {
      setProcessing(false);
    }
  };

  const handleFileInfo = async () => {
    if (!selectedFile) {
      setError("Please select a .ppc file first");
      return;
    }

    // Check if file is a .ppc file
    if (!selectedFile.name.endsWith('.ppc')) {
      setError("Please select a .ppc file to view information");
      return;
    }

    setProcessing(true);
    setError(null);
    setResult(null);

    try {
      // First upload the file to the server
      const formData = new FormData();
      formData.append('file', selectedFile);

      const uploadResponse = await fetch('http://localhost:8000/api/documents/upload', {
        method: 'POST',
        body: formData,
      });

      if (!uploadResponse.ok) {
        throw new Error("Failed to upload file");
      }

      // Now get the file info
      const filename = encodeURIComponent(selectedFile.name);
      const response = await fetch(`http://localhost:8000/api/documents/info/${filename}`);

      if (response.ok) {
        const data = await response.json();
        setResult({
          type: "info",
          message: data.message || "File information retrieved successfully!",
          details: {
            action: "info",
            filename: data.filename,
            originalFilename: data.original_filename,
            originalSize: data.original_size,
            compressedSize: data.compressed_size,
            compressionRatio: data.compression_ratio,
            compressionAlgorithm: data.compression_algorithm,
            encryptionMethod: data.encryption_method,
            fileType: data.file_type,
            mimeType: data.mime_type,
            createdAt: data.created_at
          }
        });
      } else {
        const errorData = await response.json();
        setError(errorData.error || "Failed to retrieve file information");
      }
    } catch (err) {
      console.error("File info error:", err);
      setError("Network error: " + err.message + ". Please check if the API server is running.");
    } finally {
      setProcessing(false);
    }
  };

  const handleTryDemo = async () => {
    console.log("Try Demo button clicked");
    setProcessing(true);
    setError(null);
    setResult(null);

    try {
      // Create a sample text file as a Blob
      const sampleContent = `Land Document Sample

Property Address: 123 Main Street, Anytown, ST 12345
Owner: John Doe
Parcel Number: 123-456-789
Lot Size: 0.5 acres
Zoning: Residential

This is a sample land document for demonstration purposes.`;
      
      const sampleFile = new Blob([sampleContent], { type: 'text/plain' });
      const file = new File([sampleFile], "sample_land_document.txt", {
        type: "text/plain",
      });
      
      setSelectedFile(file);
      
      setResult({
        type: "success",
        message: "Demo file created successfully!",
        details: {
          action: "demo",
          filename: "sample_land_document.txt",
          size: sampleContent.length
        }
      });
    } catch (err) {
      setError("Failed to create demo file: " + err.message);
    } finally {
      setProcessing(false);
    }
  };

  return (
    <div className="min-h-screen scroll-smooth bg-gradient-to-b from-purple-950 via-gray-900 to-black text-white overflow-hidden font-sans">
      {/* Navbar */}
      <motion.nav
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.7 }}
        className="w-full py-6 px-6 flex justify-between items-center sticky top-0 backdrop-blur-xl bg-white/5 z-50 border-b border-white/10"
      >
        <div className="flex items-center space-x-2">
          <Shield className="w-8 h-8 text-purple-400" />
          <h1 className="text-2xl font-bold tracking-wide bg-gradient-to-r from-purple-400 to-violet-500 text-transparent bg-clip-text">
            LandGuard & PCC
          </h1>
        </div>
        
        <div className="space-x-6 hidden md:block">
          <a className="hover:text-purple-300 transition" href="#features">Features</a>
          <a className="hover:text-purple-300 transition" href="#how-it-works">How It Works</a>
          <a className="hover:text-purple-300 transition" href="#technology">Technology</a>
        </div>
        
        <div className="flex space-x-4">
          <Button variant="outline" className="border-purple-500/30 text-purple-300 hover:bg-purple-500/10">
            <Github className="w-4 h-4 mr-2" />
            GitHub
          </Button>
          <Button className="bg-gradient-to-r from-purple-500 to-violet-500 hover:from-purple-400 hover:to-violet-400 text-white font-semibold px-4 py-2 rounded-xl">
            Get Started
          </Button>
        </div>
      </motion.nav>

      {/* Hero Section */}
      <section className="relative w-full flex flex-col items-center text-center px-6 pt-10 pb-20">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          className="max-w-4xl"
        >
          <Badge variant="secondary" className="mb-6 bg-purple-500/10 text-purple-300 border-purple-500/30">
            Secure Document Processing Platform
          </Badge>
          
          <h1 className="text-4xl md:text-6xl font-extrabold leading-tight mb-6 bg-gradient-to-r from-purple-300 via-violet-400 to-purple-200 text-transparent bg-clip-text">
            Secure Land Document<br />Processing & Compression
          </h1>

          <p className="text-lg md:text-xl text-gray-300 max-w-3xl mb-8 mx-auto">
            LandGuard & PCC combines AI-powered fraud detection with military-grade encryption and blockchain verification 
            to protect your critical land documents with unprecedented security.
          </p>

          {/* File Upload and Controls */}
          <Card id="file-upload-section" className="bg-white/5 border-white/10 mb-12 max-w-2xl mx-auto">            <CardHeader>
              <CardTitle className="text-purple-300 flex items-center justify-center">
                <Upload className="w-5 h-5 mr-2" />
                Process Your Documents
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex flex-col sm:flex-row gap-4">
                  <div className="flex-1">
                    <label className="block text-sm font-medium mb-2">Select File</label>
                    <input
                      type="file"
                      onChange={handleFileChange}
                      className="w-full px-3 py-2 bg-black/30 border border-white/20 rounded-lg text-white file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-semibold file:bg-purple-500/20 file:text-purple-300 hover:file:bg-purple-500/30"
                    />
                  </div>
                  <div className="flex-1">
                    <label className="block text-sm font-medium mb-2">Password (Optional)</label>
                    <input
                      type="password"
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      placeholder="Enter encryption password"
                      className="w-full px-3 py-2 bg-black/30 border border-white/20 rounded-lg text-white placeholder-gray-500"
                    />
                  </div>
                </div>
                
                {selectedFile && (
                  <div className="text-sm text-purple-300 animate-pulse">
                    <span className="inline-flex items-center">
                      <svg className="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg">
                        <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd"></path>
                      </svg>
                      Selected: {selectedFile.name} ({(selectedFile.size / 1024).toFixed(2)} KB)
                    </span>
                  </div>
                )}
                
                <div className="flex flex-wrap gap-3 justify-center pt-2">
                  <Button 
                    onClick={handleCompress}
                    disabled={processing || !selectedFile}
                    className="bg-gradient-to-r from-purple-500 to-violet-500 hover:from-purple-400 hover:to-violet-400 text-white font-bold"
                  >
                    {processing ? (
                      <>
                        <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-black" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                        </svg>
                        Compressing...
                      </>
                    ) : (
                      <>
                        <FileArchive className="w-4 h-4 mr-2" />
                        Compress File
                      </>
                    )}
                  </Button>
                  
                  <Button 
                    onClick={handleProcess}
                    disabled={processing || !selectedFile}
                    variant="outline"
                    className="border-purple-500/30 text-purple-300 hover:bg-purple-500/10"
                  >
                    {processing ? (
                      <>
                        <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-purple-300" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                        </svg>
                        Processing...
                      </>
                    ) : (
                      <>
                        <Shield className="w-4 h-4 mr-2" />
                        Process with LandGuard
                      </>
                    )}
                  </Button>
                  
                  {selectedFile && selectedFile.name.endsWith('.ppc') && (
                    <>
                      <Button 
                        onClick={handleDecompress}
                        disabled={processing}
                        variant="outline"
                        className="border-green-500/30 text-green-300 hover:bg-green-500/10"
                      >
                        {processing ? (
                          <>
                            <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-green-300" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                            </svg>
                            Decompressing...
                          </>
                        ) : (
                          <>
                            <Eye className="w-4 h-4 mr-2" />
                            Decompress File
                          </>
                        )}
                      </Button>
                      
                      <Button 
                        onClick={handleFileInfo}
                        disabled={processing}
                        variant="outline"
                        className="border-purple-500/30 text-purple-300 hover:bg-purple-500/10"
                      >
                        {processing ? (
                          <>
                            <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-purple-300" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                            </svg>
                            Loading Info...
                          </>
                        ) : (
                          <>
                            <FileText className="w-4 h-4 mr-2" />
                            File Info
                          </>
                        )}
                      </Button>
                    </>
                  )}
                </div>                
                {error && (
                  <div className="text-red-400 text-sm p-3 bg-red-900/20 rounded-lg animate-pulse">
                    Error: {error}
                  </div>
                )}
                
                {processing && (
                  <div className="text-purple-300 text-sm p-3 bg-purple-900/20 rounded-lg flex items-center">
                    <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-purple-300" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    Processing your request...
                  </div>
                )}
                
                {result && (
                  <div className={`text-sm p-3 rounded-lg ${
                    result.type === "success" 
                      ? "text-green-300 bg-green-900/20" 
                      : result.type === "info"
                      ? "text-purple-300 bg-purple-900/20"
                      : "text-yellow-300 bg-yellow-900/20"
                  }`}>
                    {result.message}
                    
                    {result.data && (
                      <div className="mt-2 text-xs">
                        <div>Workflow ID: {result.data.workflow_id}</div>
                        <div>Risk Score: {result.data.risk_score}/10</div>
                        <div>Anomalies: {result.data.anomalies_detected}</div>
                        <div>Compression Ratio: {result.data.compression_ratio}x</div>
                        <div>IPFS CID: {result.data.ipfs_cid}</div>
                        <div>Blockchain TX: {result.data.blockchain_tx}</div>
                      </div>
                    )}
                    
                    {result.details && (
                      <div className="mt-2 text-xs">
                        {result.details.action === "compress" && (
                          <>
                            <div>File: {result.details.filename}</div>
                            <div>Size: {(result.details.size / 1024).toFixed(2)} KB</div>
                          </>
                        )}
                        
                        {result.details.action === "decompress" && (
                          <>
                            <div>Original Filename: {result.details.originalFilename}</div>
                            <div>Output Path: {result.details.outputPath}</div>
                          </>
                        )}
                        
                        {result.details.action === "info" && (
                          <>
                            <div>Filename: {result.details.filename}</div>
                            <div>Original Filename: {result.details.originalFilename}</div>
                            <div>Original Size: {result.details.originalSize} bytes</div>
                            <div>Compressed Size: {result.details.compressedSize} bytes</div>
                            <div>Compression Ratio: {result.details.compressionRatio.toFixed(2)}%</div>
                            <div>Compression Algorithm: {result.details.compressionAlgorithm}</div>
                            <div>File Type: {result.details.fileType}</div>
                            <div>MIME Type: {result.details.mimeType}</div>
                            <div>Encryption: {result.details.encryptionMethod}</div>
                            <div>Created: {result.details.createdAt}</div>
                          </>
                        )}
                        
                        {result.details.action === "demo" && (
                          <>
                            <div>Demo file '{result.details.filename}' created successfully!</div>
                            <div>Size: {result.details.size} bytes</div>
                            <div className="mt-2">You can now use this file to test compression, processing, and other features.</div>
                          </>
                        )}
                      </div>
                    )}
                  </div>                )}
              </div>
            </CardContent>
          </Card>

          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Button 
              onClick={handleTryDemo}
              className="text-lg px-8 py-6 rounded-2xl bg-gradient-to-r from-purple-500 to-violet-500 hover:from-purple-400 hover:to-violet-400 text-white font-bold shadow-xl hover:shadow-purple-400/40 transition-all"
            >
              <Terminal className="w-5 h-5 mr-2" />
              Try Demo
            </Button>
            <Button variant="outline" className="text-lg px-8 py-6 rounded-2xl border-white/20 hover:bg-white/10 text-white font-bold">
              <Download className="w-5 h-5 mr-2" />
              Download CLI
            </Button>
          </div>
        </motion.div>

        {/* Stats Section */}
        <motion.div
          initial={{ opacity: 0, y: 40 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.3 }}
          className="grid grid-cols-2 md:grid-cols-4 gap-8 mt-16 max-w-4xl w-full"
        >
          {stats.map((stat, index) => (
            <div key={index} className="text-center">
              <div className="text-2xl font-bold text-purple-300">{stat.value}</div>
              <div className="text-gray-400 mt-2 text-sm">{stat.label}</div>
            </div>
          ))}
        </motion.div>

        {/* Floating Glow Animation */}
        <motion.div
          animate={{ y: [0, -20, 0], opacity: [0.6, 1, 0.6] }}
          transition={{ repeat: Infinity, duration: 6 }}
          className="absolute top-1/2 w-96 h-96 bg-purple-500/10 blur-3xl rounded-full pointer-events-none -z-10"
        />
      </section>

      {/* Features Section */}
      <section id="features" className="px-6 py-24 bg-gradient-to-b from-transparent to-gray-900/30">
        <div className="max-w-6xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6 }}
            className="text-center mb-20"
          >
            <h2 className="text-4xl font-bold mb-4">Powerful Security Features</h2>
            <p className="text-gray-400 max-w-2xl mx-auto">
              LandGuard & PCC provides enterprise-grade security through multiple layers of protection
            </p>
          </motion.div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            {features.map((feature, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 40 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.6, delay: index * 0.1 }}
                whileHover={{ y: -10 }}
                className="p-6 rounded-2xl bg-white/5 border border-white/10 shadow-xl hover:shadow-purple-400/20 transition-all"
              >
                <div className="text-purple-400 mb-4">
                  {feature.icon}
                </div>
                <h3 className="text-xl font-semibold mb-3 text-purple-300">{feature.title}</h3>
                <p className="text-gray-300">{feature.description}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* How It Works Section */}
      <section id="how-it-works" className="px-6 py-24">
        <div className="max-w-6xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6 }}
            className="text-center mb-20"
          >
            <h2 className="text-4xl font-bold mb-4">How LandGuard Works</h2>
            <p className="text-gray-400 max-w-2xl mx-auto">
              Our streamlined process ensures your documents are protected with minimal effort
            </p>
          </motion.div>

          <div className="relative">
            <div className="absolute left-1/2 transform -translate-x-1/2 h-full w-1 bg-gradient-to-b from-purple-500/20 to-transparent"></div>
            
            <div className="space-y-12">
              {steps.map((step, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, x: index % 2 === 0 ? -50 : 50 }}
                  whileInView={{ opacity: 1, x: 0 }}
                  viewport={{ once: true }}
                  transition={{ duration: 0.6, delay: index * 0.2 }}
                  className={`relative flex items-center ${index % 2 === 0 ? 'flex-row' : 'flex-row-reverse'} ${
                    index === steps.length - 1 ? '' : 'pb-12'
                  }`}
                >
                  <div className="flex-1 px-8">
                    <Card className="bg-white/5 border-white/10">
                      <CardHeader>
                        <CardTitle className="text-purple-300">Step {index + 1}</CardTitle>
                      </CardHeader>
                      <CardContent>
                        <h3 className="text-xl font-semibold mb-2">{step.title}</h3>
                        <p className="text-gray-300">{step.description}</p>
                      </CardContent>
                    </Card>
                  </div>
                  
                  <div className="absolute left-1/2 transform -translate-x-1/2 w-8 h-8 rounded-full bg-purple-500 flex items-center justify-center z-10">
                    <div className="w-4 h-4 rounded-full bg-white"></div>
                  </div>
                  
                  <div className="flex-1"></div>
                </motion.div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* Technology Stack */}
      <section id="technology" className="px-6 py-24 bg-white/5 border-y border-white/10">
        <div className="max-w-6xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6 }}
            className="text-center mb-20"
          >
            <h2 className="text-4xl font-bold mb-4">Enterprise Technology Stack</h2>
            <p className="text-gray-400 max-w-2xl mx-auto">
              Built with cutting-edge technologies for maximum security and performance
            </p>
          </motion.div>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            <motion.div
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.6 }}
              className="p-6 rounded-2xl bg-gradient-to-br from-purple-500/10 to-violet-500/10 border border-purple-500/20"
            >
              <Database className="w-12 h-12 text-purple-400 mb-4" />
              <h3 className="text-xl font-semibold mb-2">Python Backend</h3>
              <p className="text-gray-300">Robust core processing with advanced libraries</p>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.6, delay: 0.1 }}
              className="p-6 rounded-2xl bg-gradient-to-br from-purple-500/10 to-pink-500/10 border border-purple-500/20"
            >
              <Brain className="w-12 h-12 text-purple-400 mb-4" />
              <h3 className="text-xl font-semibold mb-2">AI/ML Algorithms</h3>
              <p className="text-gray-300">Machine learning for fraud detection</p>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.6, delay: 0.2 }}
              className="p-6 rounded-2xl bg-gradient-to-br from-green-500/10 to-emerald-500/10 border border-green-500/20"
            >
              <Lock className="w-12 h-12 text-green-400 mb-4" />
              <h3 className="text-xl font-semibold mb-2">AES-256 Encryption</h3>
              <p className="text-gray-300">Military-grade cryptographic security</p>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.6, delay: 0.3 }}
              className="p-6 rounded-2xl bg-gradient-to-br from-orange-500/10 to-red-500/10 border border-orange-500/20"
            >
              <Globe className="w-12 h-12 text-orange-400 mb-4" />
              <h3 className="text-xl font-semibold mb-2">IPFS & Blockchain</h3>
              <p className="text-gray-300">Decentralized storage and verification</p>
            </motion.div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="px-6 py-32">
        <div className="max-w-4xl mx-auto text-center">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6 }}
          >
            <h2 className="text-4xl md:text-5xl font-bold mb-6">
              Ready to Secure Your<br />Land Documents?
            </h2>
            <p className="text-xl text-gray-300 mb-12 max-w-2xl mx-auto">
              Join thousands of professionals who trust LandGuard & PCC for their most critical document security needs.
            </p>
            
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Button className="text-lg px-10 py-6 rounded-2xl bg-gradient-to-r from-purple-500 to-violet-500 hover:from-purple-400 hover:to-violet-400 text-white font-bold shadow-xl hover:shadow-purple-400/40 transition-all">
                Get Started Free
              </Button>
              <Button variant="outline" className="text-lg px-10 py-6 rounded-2xl border-white/20 hover:bg-white/10 text-white font-bold">
                Schedule Demo
              </Button>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Footer */}
      <footer className="text-center py-12 text-gray-400 border-t border-white/10">
        <div className="max-w-6xl mx-auto px-6">
          <div className="flex flex-col md:flex-row justify-between items-center">
            <div className="flex items-center space-x-2 mb-4 md:mb-0">
              <Shield className="w-6 h-6 text-purple-400" />
              <span className="font-semibold">LandGuard & PCC</span>
            </div>
            <div className="flex space-x-6">
              <a href="#" className="hover:text-purple-300 transition">Documentation</a>
              <a href="#" className="hover:text-purple-300 transition">API</a>
              <a href="#" className="hover:text-purple-300 transition">GitHub</a>
              <a href="#" className="hover:text-purple-300 transition">Support</a>
            </div>
          </div>
          <div className="mt-8 pt-8 border-t border-white/10 text-sm">
            © {new Date().getFullYear()} LandGuard & PCC. All rights reserved. Secure document processing platform.
          </div>
        </div>
      </footer>
    </div>
  );
}